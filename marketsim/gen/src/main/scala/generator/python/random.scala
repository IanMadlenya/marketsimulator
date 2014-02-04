package generator.python
import predef._

object random extends gen.PythonGenerator
{
    import base.Def

    case class Parameter(p : Typed.Parameter) extends base.Parameter

    case class Import(f : Typed.Function)
            extends base.Intrinsic
            with    base.DocString
    {
        val name = f.name
        val parameters = f.parameters map Parameter
        val alias = f.docstring.get.brief
        val rv_type = "float"
        val args = Nil
        override def base_class = s"Function[$rv_type]" |||
                                ImportFrom("Function", "marketsim.ops._function")

        override val category = "Random"

        type Parameter = random.Parameter

        def casts_to = Def("_casts_to", "dst", s"return $name._types[0]._casts_to(dst)")


        val impl_module = "random"

        override def body = super.body | call | casts_to
    }

    def generatePython(/** arguments of the annotation */ args  : List[String])
                      (/** function to process         */ f     : Typed.Function) =
    {
        new Import(f)
    }

    val name = "python.random"

}
