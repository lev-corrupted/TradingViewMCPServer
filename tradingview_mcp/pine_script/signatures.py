"""
Pine Script Function Signature Database

Comprehensive database of all Pine Script built-in functions with parameter validation.
Supports Pine Script v4 and v5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Set
from enum import Enum


class ParamType(Enum):
    """Parameter type qualifiers"""
    SERIES = "series"
    SIMPLE = "simple"
    CONST = "const"
    INPUT = "input"
    ANY = "any"


class DataType(Enum):
    """Data types in Pine Script"""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    COLOR = "color"
    STRING = "string"
    LINE = "line"
    LABEL = "label"
    BOX = "box"
    TABLE = "table"
    ARRAY = "array"
    MATRIX = "matrix"
    ANY = "any"


@dataclass
class FunctionParameter:
    """Represents a function parameter"""
    name: str
    data_type: DataType
    param_type: ParamType = ParamType.SERIES
    optional: bool = False
    default_value: Optional[Any] = None
    description: str = ""


@dataclass
class FunctionSignature:
    """Represents a complete function signature"""
    name: str
    parameters: List[FunctionParameter]
    return_type: DataType
    namespace: Optional[str] = None  # e.g., 'ta', 'math', 'str'
    version: int = 4  # Minimum version required
    deprecated: bool = False
    replacement: Optional[str] = None
    description: str = ""
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []

    @property
    def full_name(self) -> str:
        """Get full function name with namespace"""
        if self.namespace:
            return f"{self.namespace}.{self.name}"
        return self.name


class FunctionSignatureDB:
    """
    Database of all Pine Script built-in function signatures.

    Provides validation and documentation for function calls.
    """

    def __init__(self):
        self.functions: Dict[str, FunctionSignature] = {}
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the function signature database"""

        # ===== PLOT FUNCTIONS =====

        self.functions["plot"] = FunctionSignature(
            name="plot",
            parameters=[
                FunctionParameter("series", DataType.FLOAT, ParamType.SERIES, description="Series of values to plot"),
                FunctionParameter("title", DataType.STRING, ParamType.CONST, optional=True, description="Plot title"),
                FunctionParameter("color", DataType.COLOR, ParamType.SERIES, optional=True, description="Plot color"),
                FunctionParameter("linewidth", DataType.INT, ParamType.INPUT, optional=True, default_value=1, description="Line width"),
                FunctionParameter("style", DataType.INT, ParamType.INPUT, optional=True, description="Plot style"),
                FunctionParameter("trackprice", DataType.BOOL, ParamType.INPUT, optional=True, default_value=False, description="Track price on scale"),
                FunctionParameter("show_last", DataType.INT, ParamType.INPUT, optional=True, description="Show last N bars"),
                FunctionParameter("offset", DataType.INT, ParamType.INPUT, optional=True, default_value=0, description="Offset in bars"),
            ],
            return_type=DataType.ANY,
            version=1,
            description="Plots a series of data on the chart",
            examples=["plot(close)", "plot(close, color=color.red, linewidth=2)"],
        )

        # ===== TECHNICAL ANALYSIS (v5 namespace) =====

        self.functions["ta.sma"] = FunctionSignature(
            name="sma",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Simple Moving Average",
            examples=["ta.sma(close, 20)", "ta.sma(volume, 10)"],
        )

        self.functions["ta.ema"] = FunctionSignature(
            name="ema",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Exponential Moving Average",
            examples=["ta.ema(close, 20)"],
        )

        self.functions["ta.rsi"] = FunctionSignature(
            name="rsi",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Relative Strength Index",
            examples=["ta.rsi(close, 14)"],
        )

        self.functions["ta.macd"] = FunctionSignature(
            name="macd",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("fast", DataType.INT, ParamType.SIMPLE, description="Fast length"),
                FunctionParameter("slow", DataType.INT, ParamType.SIMPLE, description="Slow length"),
                FunctionParameter("signal", DataType.INT, ParamType.SIMPLE, description="Signal length"),
            ],
            return_type=DataType.ANY,  # Returns tuple
            version=5,
            description="Moving Average Convergence Divergence",
            examples=["[macd, signal, hist] = ta.macd(close, 12, 26, 9)"],
        )

        self.functions["ta.stoch"] = FunctionSignature(
            name="stoch",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("high", DataType.FLOAT, ParamType.SERIES, description="High series"),
                FunctionParameter("low", DataType.FLOAT, ParamType.SERIES, description="Low series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Stochastic Oscillator",
            examples=["ta.stoch(close, high, low, 14)"],
        )

        self.functions["ta.atr"] = FunctionSignature(
            name="atr",
            namespace="ta",
            parameters=[
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Average True Range",
            examples=["ta.atr(14)"],
        )

        self.functions["ta.bb"] = FunctionSignature(
            name="bb",
            namespace="ta",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
                FunctionParameter("mult", DataType.FLOAT, ParamType.SIMPLE, description="Standard deviation multiplier"),
            ],
            return_type=DataType.ANY,  # Returns tuple
            version=5,
            description="Bollinger Bands",
            examples=["[middle, upper, lower] = ta.bb(close, 20, 2.0)"],
        )

        # ===== MATH FUNCTIONS (v5 namespace) =====

        self.functions["math.abs"] = FunctionSignature(
            name="abs",
            namespace="math",
            parameters=[
                FunctionParameter("x", DataType.FLOAT, ParamType.SERIES, description="Value"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Absolute value",
            examples=["math.abs(-10)"],
        )

        self.functions["math.max"] = FunctionSignature(
            name="max",
            namespace="math",
            parameters=[
                FunctionParameter("x", DataType.FLOAT, ParamType.SERIES, description="First value"),
                FunctionParameter("y", DataType.FLOAT, ParamType.SERIES, description="Second value"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Maximum of two values",
            examples=["math.max(close, open)"],
        )

        self.functions["math.min"] = FunctionSignature(
            name="min",
            namespace="math",
            parameters=[
                FunctionParameter("x", DataType.FLOAT, ParamType.SERIES, description="First value"),
                FunctionParameter("y", DataType.FLOAT, ParamType.SERIES, description="Second value"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Minimum of two values",
            examples=["math.min(close, open)"],
        )

        self.functions["math.round"] = FunctionSignature(
            name="round",
            namespace="math",
            parameters=[
                FunctionParameter("x", DataType.FLOAT, ParamType.SERIES, description="Value to round"),
                FunctionParameter("precision", DataType.INT, ParamType.SIMPLE, optional=True, default_value=0, description="Decimal places"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Round to nearest integer or specified precision",
            examples=["math.round(close)", "math.round(close, 2)"],
        )

        # ===== INPUT FUNCTIONS =====

        self.functions["input.int"] = FunctionSignature(
            name="int",
            namespace="input",
            parameters=[
                FunctionParameter("defval", DataType.INT, ParamType.CONST, description="Default value"),
                FunctionParameter("title", DataType.STRING, ParamType.CONST, optional=True, description="Input title"),
                FunctionParameter("minval", DataType.INT, ParamType.CONST, optional=True, description="Minimum value"),
                FunctionParameter("maxval", DataType.INT, ParamType.CONST, optional=True, description="Maximum value"),
                FunctionParameter("step", DataType.INT, ParamType.CONST, optional=True, default_value=1, description="Step size"),
            ],
            return_type=DataType.INT,
            version=4,
            description="Integer input parameter",
            examples=['input.int(14, "Period", minval=1, maxval=100)'],
        )

        self.functions["input.float"] = FunctionSignature(
            name="float",
            namespace="input",
            parameters=[
                FunctionParameter("defval", DataType.FLOAT, ParamType.CONST, description="Default value"),
                FunctionParameter("title", DataType.STRING, ParamType.CONST, optional=True, description="Input title"),
                FunctionParameter("minval", DataType.FLOAT, ParamType.CONST, optional=True, description="Minimum value"),
                FunctionParameter("maxval", DataType.FLOAT, ParamType.CONST, optional=True, description="Maximum value"),
                FunctionParameter("step", DataType.FLOAT, ParamType.CONST, optional=True, description="Step size"),
            ],
            return_type=DataType.FLOAT,
            version=4,
            description="Float input parameter",
            examples=['input.float(2.0, "Multiplier", minval=0.1, step=0.1)'],
        )

        self.functions["input.bool"] = FunctionSignature(
            name="bool",
            namespace="input",
            parameters=[
                FunctionParameter("defval", DataType.BOOL, ParamType.CONST, description="Default value"),
                FunctionParameter("title", DataType.STRING, ParamType.CONST, optional=True, description="Input title"),
            ],
            return_type=DataType.BOOL,
            version=4,
            description="Boolean input parameter",
            examples=['input.bool(true, "Show MA")'],
        )

        # ===== DEPRECATED FUNCTIONS (v4 and older) =====

        self.functions["sma"] = FunctionSignature(
            name="sma",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=4,
            deprecated=True,
            replacement="ta.sma",
            description="Simple Moving Average (deprecated, use ta.sma)",
        )

        self.functions["ema"] = FunctionSignature(
            name="ema",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=4,
            deprecated=True,
            replacement="ta.ema",
            description="Exponential Moving Average (deprecated, use ta.ema)",
        )

        self.functions["rsi"] = FunctionSignature(
            name="rsi",
            parameters=[
                FunctionParameter("source", DataType.FLOAT, ParamType.SERIES, description="Source series"),
                FunctionParameter("length", DataType.INT, ParamType.SIMPLE, description="Number of bars"),
            ],
            return_type=DataType.FLOAT,
            version=4,
            deprecated=True,
            replacement="ta.rsi",
            description="Relative Strength Index (deprecated, use ta.rsi)",
        )

        self.functions["study"] = FunctionSignature(
            name="study",
            parameters=[
                FunctionParameter("title", DataType.STRING, ParamType.CONST, description="Indicator title"),
                FunctionParameter("shorttitle", DataType.STRING, ParamType.CONST, optional=True, description="Short title"),
                FunctionParameter("overlay", DataType.BOOL, ParamType.CONST, optional=True, default_value=False, description="Overlay on chart"),
            ],
            return_type=DataType.ANY,
            version=3,
            deprecated=True,
            replacement="indicator",
            description="Study declaration (deprecated, use indicator)",
        )

        self.functions["indicator"] = FunctionSignature(
            name="indicator",
            parameters=[
                FunctionParameter("title", DataType.STRING, ParamType.CONST, description="Indicator title"),
                FunctionParameter("shorttitle", DataType.STRING, ParamType.CONST, optional=True, description="Short title"),
                FunctionParameter("overlay", DataType.BOOL, ParamType.CONST, optional=True, default_value=False, description="Overlay on chart"),
                FunctionParameter("format", DataType.STRING, ParamType.CONST, optional=True, description="Price format"),
                FunctionParameter("precision", DataType.INT, ParamType.CONST, optional=True, description="Decimal precision"),
            ],
            return_type=DataType.ANY,
            version=5,
            description="Indicator declaration",
            examples=['indicator("My Indicator", overlay=true)'],
        )

        # ===== STRATEGY FUNCTIONS =====

        self.functions["strategy"] = FunctionSignature(
            name="strategy",
            parameters=[
                FunctionParameter("title", DataType.STRING, ParamType.CONST, description="Strategy title"),
                FunctionParameter("shorttitle", DataType.STRING, ParamType.CONST, optional=True, description="Short title"),
                FunctionParameter("overlay", DataType.BOOL, ParamType.CONST, optional=True, default_value=False, description="Overlay on chart"),
                FunctionParameter("initial_capital", DataType.FLOAT, ParamType.CONST, optional=True, default_value=10000, description="Initial capital"),
                FunctionParameter("commission_type", DataType.STRING, ParamType.CONST, optional=True, description="Commission type"),
                FunctionParameter("commission_value", DataType.FLOAT, ParamType.CONST, optional=True, description="Commission value"),
            ],
            return_type=DataType.ANY,
            version=1,
            description="Strategy declaration",
            examples=['strategy("My Strategy", overlay=true, initial_capital=10000)'],
        )

        # ===== STRING FUNCTIONS (v5) =====

        self.functions["str.tostring"] = FunctionSignature(
            name="tostring",
            namespace="str",
            parameters=[
                FunctionParameter("value", DataType.ANY, ParamType.SERIES, description="Value to convert"),
                FunctionParameter("format", DataType.STRING, ParamType.CONST, optional=True, description="Format string"),
            ],
            return_type=DataType.STRING,
            version=5,
            description="Convert value to string",
            examples=["str.tostring(close)", 'str.tostring(close, "#.##")'],
        )

        self.functions["str.tonumber"] = FunctionSignature(
            name="tonumber",
            namespace="str",
            parameters=[
                FunctionParameter("string", DataType.STRING, ParamType.SERIES, description="String to convert"),
            ],
            return_type=DataType.FLOAT,
            version=5,
            description="Convert string to number",
            examples=['str.tonumber("42.5")'],
        )

        # ===== ARRAY FUNCTIONS (v5) =====

        self.functions["array.new_float"] = FunctionSignature(
            name="new_float",
            namespace="array",
            parameters=[
                FunctionParameter("size", DataType.INT, ParamType.SIMPLE, optional=True, default_value=0, description="Array size"),
                FunctionParameter("initial_value", DataType.FLOAT, ParamType.SERIES, optional=True, description="Initial value"),
            ],
            return_type=DataType.ARRAY,
            version=5,
            description="Create new float array",
            examples=["array.new_float(10, 0.0)"],
        )

        self.functions["array.push"] = FunctionSignature(
            name="push",
            namespace="array",
            parameters=[
                FunctionParameter("array", DataType.ARRAY, ParamType.SERIES, description="Array to modify"),
                FunctionParameter("value", DataType.ANY, ParamType.SERIES, description="Value to add"),
            ],
            return_type=DataType.ANY,
            version=5,
            description="Add element to end of array",
            examples=["array.push(myArray, close)"],
        )

    def get_function(self, name: str) -> Optional[FunctionSignature]:
        """Get function signature by name"""
        return self.functions.get(name)

    def get_all_functions(self, version: int = 5) -> List[FunctionSignature]:
        """Get all functions available in a specific version"""
        return [
            func for func in self.functions.values()
            if func.version <= version
        ]

    def search_functions(self, query: str) -> List[FunctionSignature]:
        """Search for functions by name or description"""
        query_lower = query.lower()
        return [
            func for func in self.functions.values()
            if query_lower in func.name.lower()
            or query_lower in func.description.lower()
            or (func.namespace and query_lower in func.namespace.lower())
        ]

    def validate_call(
        self,
        function_name: str,
        arguments: List[Any],
        named_arguments: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """
        Validate a function call.

        Args:
            function_name: Name of the function
            arguments: Positional arguments
            named_arguments: Named arguments

        Returns:
            (is_valid, error_messages)
        """
        func = self.get_function(function_name)

        if not func:
            return False, [f"Unknown function: '{function_name}'"]

        errors = []

        # Check if function is deprecated
        if func.deprecated:
            errors.append(
                f"Function '{function_name}' is deprecated. "
                f"Use '{func.replacement}' instead."
            )

        # Get required parameters
        required_params = [p for p in func.parameters if not p.optional]

        # Check argument count
        total_provided = len(arguments) + len(named_arguments)
        if total_provided < len(required_params):
            errors.append(
                f"Function '{function_name}' requires {len(required_params)} arguments, "
                f"but {total_provided} were provided."
            )

        if len(arguments) > len(func.parameters):
            errors.append(
                f"Function '{function_name}' accepts at most {len(func.parameters)} arguments, "
                f"but {len(arguments)} were provided."
            )

        # Validate named arguments
        param_names = {p.name for p in func.parameters}
        for name in named_arguments:
            if name not in param_names:
                errors.append(
                    f"Unknown parameter '{name}' for function '{function_name}'. "
                    f"Valid parameters: {', '.join(param_names)}"
                )

        return len(errors) == 0, errors

    def get_function_help(self, function_name: str) -> Optional[str]:
        """Get formatted help text for a function"""
        func = self.get_function(function_name)

        if not func:
            return None

        help_text = f"**{func.full_name}**\n\n"
        help_text += f"{func.description}\n\n"

        if func.deprecated:
            help_text += f"⚠️ **DEPRECATED**: Use `{func.replacement}` instead.\n\n"

        help_text += "**Parameters:**\n"
        for param in func.parameters:
            optional_str = " (optional)" if param.optional else ""
            default_str = f", default: {param.default_value}" if param.default_value is not None else ""
            help_text += f"- `{param.name}` ({param.data_type.value}){optional_str}{default_str}: {param.description}\n"

        help_text += f"\n**Returns:** {func.return_type.value}\n"

        if func.examples:
            help_text += "\n**Examples:**\n"
            for example in func.examples:
                help_text += f"```pine\n{example}\n```\n"

        return help_text
