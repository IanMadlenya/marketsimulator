package generator.python
import predef._

package object base {

    val tab = "    "
    val comma = ","

    object Annotations
    {
        import Typed.Annotations._

        override def toString = registry.toString()

        // TODO: non-intrusive registration
        register(random)
        register(mathops)
    }

    abstract class Parameter {

        val p : Typed.Parameter

        def name = p.name
        def ty = "float"
        def s_initializer = p.initializer.toString

        def init = s"$name = $s_initializer"
        def assign = s"self.$name = $name"
        def property = s"\'$name\' : $ty"
        def repr = s"""$name = \"+repr(self.$name)+\" """
        def call = s"self.$name"
    }

    abstract class Printer() {
        type Parameter <: base.Parameter
        def name        : String
        def docstring   : String
        def alias       : String
        def category    : String
        def parameters  : List[Parameter]
        val filename    : String

        def registration = s"@registry.expose(['$category', '$alias'])"
        def base_class = "object"

        def join_fields(p : Parameter => String, sep : String = ", ") = parameters map p mkString sep

        def init_fields = join_fields({ _.init })
        def assign_fields = join_fields({ _.assign }, crlf)
        def property_fields = join_fields({ _.property }, comma + crlf)
        def repr_fields = join_fields({ _.repr })
        def call_fields = join_fields({ _.call })

        def impl_function = name

        def header = "" | registration |
            s"class $name($base_class):" | nl

        def doc = s"""$tab\"\"\" ${docstring.replaceAll(crlf, crlf+tab)}$crlf$tab\"\"\" """

        def init_body = assign_fields

        def init = indent { s"def __init__(self, $init_fields):" |> init_body | nl }

        def label = indent {
            "@property" |
            "def label(self):" |>
                "return repr(self)" |
            nl
        }

        def properties = indent {
            "_properties = {" |> property_fields | "}" | nl
        }

        def repr_body = s"""return "$name($repr_fields)" """

        def repr = indent { "def __repr__(self):" |> repr_body | nl }

        def impl_module : String

        def call_body = s"""return $impl_module.$impl_function($call_fields)"""

        def call = indent {
            "def __call__(self, *args, **kwargs):" |> call_body | nl
        }

        def prologue : String

        override def toString = s"""$header$doc$init$label$properties$repr"""
    }

}
