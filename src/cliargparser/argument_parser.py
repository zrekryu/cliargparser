from collections.abc import Callable, Iterable
import shlex
from typing import Any, assert_never

from .enums import NArgs, OptionPrefix, OptionToken, ParseMode, ParsingSentinel
from .exceptions import (
    ExtraOperandError,
    MissingOperandArgumentsError,
    MissingOptionArgumentsError,
    OptionInGroupTakesArgumentsError,
    OptionTakesNoArgumentError,
    UnknownCommandError,
    UnknownLongOptionError,
    UnknownShortOptionError,
    UnknownShortOptionInGroupError,
)
from .models import Namespace, ParseContext, TokenStream
from .models.arguments import Command, Option


class ArgumentParser:
    @classmethod
    def parse_arguments(
        cls, arguments: str | Iterable[str], command: Command
    ) -> Namespace:
        if isinstance(arguments, str):
            arguments = shlex.split(arguments)

        token_stream = TokenStream(arguments)
        namespace = Namespace()

        context = ParseContext(
            command=command,
            namespace=namespace,
            token_stream=token_stream,
        )

        while (token := token_stream.consume()) is not None:
            if not context.end_of_options and token == ParsingSentinel.END_OF_OPTIONS:
                context.end_of_options = True
                continue

            if not context.end_of_options:
                if token.startswith(OptionPrefix.LONG):
                    cls._parse_long_option(token, context)
                    continue
                elif token.startswith(OptionPrefix.SHORT):
                    cls._parse_short_option(token, context)
                    continue

            if context.command.parse_mode is ParseMode.COMMAND:
                cls._parse_command(token, context)
                continue
            elif context.command.parse_mode is ParseMode.OPERAND:
                cls._parse_operand(token, context)
                continue
            else:
                assert_never(context.command.parse_mode)

        return namespace

    @classmethod
    def _parse_long_option(cls, token: str, context: ParseContext) -> None:
        explicit_argument: str | None
        name, sep, explicit_argument = (
            token
            .removeprefix(OptionPrefix.LONG)
            .partition(OptionToken.EXPLICIT_ARGUMENT)
        )
        if not sep:
            explicit_argument = None

        option_name_with_prefix = f"{OptionPrefix.LONG}{name}"

        option = context.command.get_option(name)
        if not option:
            raise UnknownLongOptionError(name)

        values = cls._consume_and_validate_option_arguments(
            option=option,
            context=context,
            explicit_argument=explicit_argument,
            token=token,
            option_name_with_prefix=option_name_with_prefix
        )

        context.namespace[option.store_name] = option.action(
            option, values, context.namespace.get(option.store_name)
        )

    @classmethod
    def _parse_short_option(cls, token: str, context: ParseContext) -> None:
        option_token_without_prefix, *_ = (
            token
            .removeprefix(OptionPrefix.SHORT)
            .partition(OptionToken.EXPLICIT_ARGUMENT)
        )
        if len(option_token_without_prefix) > 1:
            cls._parse_short_option_group(option_token_without_prefix, context)
        else:
            cls._parse_single_short_option(token, context)

    @classmethod
    def _parse_single_short_option(cls, token: str, context: ParseContext) -> None:
        explicit_argument: str | None
        name, sep, explicit_argument = (
            token
            .removeprefix(OptionPrefix.SHORT)
            .partition(OptionToken.EXPLICIT_ARGUMENT)
        )
        if not sep:
            explicit_argument = None

        option_name_with_prefix = f"{OptionPrefix.SHORT}{name}"

        option = context.command.get_option(name)
        if not option:
            raise UnknownShortOptionError(name)

        values = cls._consume_and_validate_option_arguments(
            option=option,
            context=context,
            explicit_argument=explicit_argument,
            token=token,
            option_name_with_prefix=option_name_with_prefix
        )

        context.namespace[option.store_name] = option.action(
            option, values, context.namespace.get(option.store_name)
        )

    @classmethod
    def _parse_short_option_group(cls, group: str, context: ParseContext) -> None:
        for option_token in group:
            option = context.command.get_option(option_token)
            if not option:
                raise UnknownShortOptionInGroupError(option_token, group)

            if option.takes_arguments:
                raise OptionInGroupTakesArgumentsError(option_token, group)

            context.namespace[option.store_name] = option.action(
                option, (), context.namespace.get(option.store_name)
            )

    @classmethod
    def _consume_and_validate_option_arguments(
        cls,
        option: Option,
        context: ParseContext,
        *,
        explicit_argument: str | None = None,
        token: str,
        option_name_with_prefix: str,
    ) -> list[str]:
        if not option.takes_arguments and explicit_argument is not None:
            raise OptionTakesNoArgumentError(option_name_with_prefix, explicit_argument)

        values: list[Any]
        if option.takes_arguments:
            if explicit_argument is not None:
                values = [explicit_argument]
            else:
                values = cls._consume_arguments(
                    option.nargs, context, type_converter=option.type_converter
                )
        else:
            values = []

        if not cls._is_nargs_satisfied(option.nargs, len(values)):
            raise MissingOptionArgumentsError(
                token, option.nargs, len(values)
            )

        return values

    @staticmethod
    def _parse_command(token: str, context: ParseContext) -> None:
        command = context.command.get_subcommand(token)
        if not command:
            raise UnknownCommandError(token)

        context.command = command

        command_namespace = Namespace()
        context.namespace[command.name] = command_namespace
        context.namespace = command_namespace

    @classmethod
    def _parse_operand(cls, token: str, context: ParseContext) -> None:
        try:
            operand = context.command.get_operand_by_index(context.operand_index)
        except IndexError:
            raise ExtraOperandError(token) from None

        values: list[Any] = [token]
        if operand.takes_arguments:
            operand_args = cls._consume_arguments(
                operand.nargs, context, type_converter=operand.type_converter
            )
            values.extend(operand_args)

        if not cls._is_nargs_satisfied(operand.nargs, len(values)):
            raise MissingOperandArgumentsError(
                operand.name, operand.nargs, len(values)
            )

        context.namespace[operand.name] = operand.action(
            operand, values, context.namespace.get(operand.name)
        )

        context.operand_index += 1

    @staticmethod
    def _consume_arguments(
        nargs: int | NArgs,
        context: ParseContext,
        *,
        type_converter: Callable[[str], Any]
    ) -> list[Any]:
        values: list[Any] = []
        while (token := context.token_stream.peek()) is not None:
            if not context.end_of_options and token.startswith(OptionPrefix.SHORT):
                break

            if isinstance(nargs, int):
                if len(values) >= nargs:
                    break
            elif nargs is NArgs.OPTIONAL and values:
                break

            values.append(type_converter(token))

            context.token_stream.consume()

        return values

    @staticmethod
    def _is_nargs_satisfied(nargs: int | NArgs, count: int) -> bool:
        if isinstance(nargs, NArgs):
            if nargs is NArgs.ONE_OR_MORE and count < 1:
                return False

            return True

        return count >= nargs