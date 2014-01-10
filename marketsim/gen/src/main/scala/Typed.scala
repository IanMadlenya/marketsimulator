package object Typed
{
    import AST.{BinOpSymbol, CondSymbol, DocString, QualifiedName}
    import syntax.scala.Printer.{typed => sc}
    import generator.python.{Printer => py}
    import predef.{ScPrintable, ScPyPrintable}

    abstract class Expr
            extends ScPyPrintable
            with    sc.Expr
            with    py.Expr
    {
        def ty : TypesBound.Base
    }

    case class Neg(x : Expr)
            extends Expr
            with    sc.Neg
            with    py.Neg
            with    TypeInference.Neg

    case class BinOp(symbol : BinOpSymbol,
                     x      : Expr,
                     y      : Expr)
            extends Expr
            with    sc.BinOp
            with    py.BinOp
            with    TypeInference.BinOp

    case class IfThenElse(cond  : Expr,
                          x     : Expr,
                          y     : Expr)
            extends Expr
            with    sc.IfThenElse
            with    py.IfThenElse
            with    TypeInference.IfThenElse

    case class StringLit(value : String)
            extends Expr
            with    sc.StringLit
            with    py.StringLit
            with    TypeInference.StringLit

    case class IntLit(value : Int)
            extends Expr
            with    sc.IntLit
            with    py.IntLit
            with    TypeInference.IntLit


    case class FloatLit(x : Double)
            extends Expr
            with    sc.FloatLit
            with    py.FloatLit
            with    TypeInference.FloatLit

    case class ParamRef(p : Parameter)
            extends Expr
            with    sc.ParamRef
            with    py.ParamRef
            with    TypeInference.ParamRef

    case class FunctionRef(f : Function)
            extends Expr
            with    sc.FunctionRef
            with    py.FunctionRef
            with    TypeInference.FunctionRef

    case class FunctionCall(target      : Expr,
                            arguments   : List[(Parameter, Expr)])
            extends Expr
            with    sc.FunCall
            with    py.FunCall
            with    TypeInference.FunctionCall

    case class Annotation(target    : AnnotationHandler,
                          parameters: List[String])
            extends sc.Annotation
            with    ScPrintable

    case class Attributes(items : Map[String, String])
            extends sc.Attributes
            with    ScPrintable

    case class Parameter(name        : String,
                         ty          : TypesBound.Base,
                         initializer : Option[Expr],
                         comment     : List[String])
            extends sc.Parameter
            with    ScPrintable

    case class Or(x : Expr,
                  y : Expr)
            extends Expr
            with    sc.Or
            with    py.Or
            with    TypeInference.BinaryBoolean

    case class And(x : Expr,
                   y : Expr)
            extends Expr
            with    sc.And
            with    py.And
            with    TypeInference.BinaryBoolean

    case class Not(x : Expr)
            extends Expr
            with    sc.Not
            with    py.Not
            with    TypeInference.UnaryBoolean

    case class Condition(symbol : CondSymbol,
                         x      : Expr,
                         y      : Expr)
            extends Expr
            with    sc.Condition
            with    py.Condition
            with    TypeInference.Condition

    case class Cast(x   : Expr,
                    ty  : TypesBound.Base)
            extends Expr
            with    sc.Cast
            with    py.Cast
    {
        if (x.ty cannotCastTo ty)
            throw new Exception(s"Expression $x cannot be casted to $ty")
    }

    case class FunctionAlias(parent : Package,
                             name   : String,
                             target : Function)
            extends sc.FunctionAlias
            with    ScPrintable

    case class Function(parent      : Package,
                        name        : String,
                        parameters  : List[Parameter],
                        ret_type    : TypesBound.Base,
                        body        : Option[Expr],
                        docstring   : Option[DocString],
                        annotations : List[Annotation],
                        attributes  : Attributes)
            extends sc.Function
            with    ScPrintable
    {
        def decorators = attributes :: annotations

        def qualifiedName = parent qualifyName name

        val first_optional = parameters indexWhere { _.initializer.nonEmpty } match {
            case -1 => parameters.length
            case idx => idx
        }

        parameters.indexWhere({ _.initializer.isEmpty}, first_optional) match {
            case -1 =>
            case idx => throw new Exception(s"A mandatory argument '${parameters(idx)}' found after optional argument '${parameters(first_optional)}' " +
                    s"at function declaration $this")
        }

        val ty = TypesBound.Function(parameters map { _.ty }, ret_type, first_optional)

        def getAttribute(name : String) = tryGetAttribute(name) match {
            case Some(v) => v
            case None =>    throw new Exception(s"Cannot find attribute '$name' for function $this")
        }
        def tryGetAttribute(name : String) = attributes.items get name match {
            case Some(v) => Some(v)
            case None =>    parent tryGetAttribute name
        }

        override def equals(o : Any) = o match {
            case that : Function =>
                parent.qualifiedName == that.parent.qualifiedName &&
                name                 == that.name &&
                parameters           == that.parameters &&
                ret_type             == that.ret_type &&
                body                 == that.body &&
                docstring            == that.docstring &&
                attributes           == that.attributes &&
                annotations          == that.annotations
            case _ => false
        }

    }


    trait TypeDeclaration
    {
        val name        : String
        val scope       : Typed.Package
        val generics    : List[TypesUnbound.Parameter]

        def resolveGenerics(genericArgs : List[TypesUnbound.Base]) : TypesUnbound.Base

        override def equals(o : Any) = o match {
            case that : TypeDeclaration => name == that.name && scope.qualifiedName == that.scope.qualifiedName
            case _ => false
        }

        def label = (scope qualifyName name) + (if (generics.isEmpty) "" else generics mkString ("[", ",", "]"))
    }

    case class AliasDecl(name       : String,
                         scope      : Typed.Package,
                         target     : TypesUnbound.Base,
                         generics   : List[TypesUnbound.Parameter])
            extends TypeDeclaration
            with    sc.AliasDecl
            with    ScPrintable
    {
        private val unbound = predef.Memoize1({
            genericArgs : List[TypesUnbound.Base] =>
                TypesUnbound.Alias(this, genericArgs)
        })
        def resolveGenerics(genericArgs : List[TypesUnbound.Base]) = unbound(genericArgs)
    }

    case class InterfaceDecl(name       : String,
                             scope      : Typed.Package,
                             bases      : List[TypesUnbound.Base],
                             generics   : List[TypesUnbound.Parameter])
            extends TypeDeclaration
            with    sc.InterfaceDecl
            with    ScPrintable
    {
        private val unbound = predef.Memoize1({
            genericArgs : List[TypesUnbound.Base] =>
                TypesUnbound.Interface(this, genericArgs)
        })
        def resolveGenerics(genericArgs : List[TypesUnbound.Base]) = unbound(genericArgs)
    }



    abstract class Package
    {
        var functions = Map[String, Function]()
        var functionAliases = Map[String, FunctionAlias]()
        var packages = Map[String, SubPackage]()
        var anonymous = List[AnonymousPackage]()
        var types = Map[String, TypeDeclaration]()
        var annotations = List[Annotation]()
        val attributes = Attributes(Map.empty)

        def qualifiedName : AST.QualifiedName
        def qualifyName(x : String) : AST.QualifiedName = AST.QualifiedName(qualifiedName.names :+ x)
        def tryGetAttribute(name : String) : Option[String]
        def getName : String

        def insert(f : Function)  = {
            functions = functions updated (f.name, f)
            f
        }

        def insert(f : FunctionAlias)  = {
            functionAliases = functionAliases updated (f.name, f)
            f
        }

        def insert(t : TypeDeclaration) = {
            types = types updated (t.name, t)
            t
        }

        def createChild(n : String, a : Attributes) = {
            val p = new SubPackage(n, this, a)
            packages = packages updated (p.name, p)
            p
        }

        def createChild(a : Attributes) = {
            anonymous find { _.attributes == a } match {
                case Some(p) => p
                case None    =>
                    val p = new AnonymousPackage(this, a)
                    anonymous = p :: anonymous
                    p
            }
        }

        override def equals(o : Any) = o match {
            case that : Package =>
                (functions       equals that.functions) &&
                (functionAliases equals that.functionAliases) &&
                (packages        equals that.packages)  &&
                (anonymous       equals that.anonymous) &&
                (attributes      equals that.attributes)
            case _ => false
        }

        def getOrElseUpdateFunction(name : String, default : => Typed.Function) =
            functions get name match {
                case Some(f) => f
                case None => insert(default)
            }

        def getOrElseUpdateFunctionAlias(name : String, default : => Typed.FunctionAlias) =
            functionAliases get name match {
                case Some(f) => f
                case None => insert(default)
            }

        protected def getFunctionImpl(name : String) =
            functions get name match {
                case Some(f) => Some(f)
                case None    =>
                    functionAliases get name match {
                        case Some(a) => Some(a.target)
                        case None    => None
                    }

            }

        def getFunction(name : String) = getFunctionImpl(name)

        def getOrElseUpdateType(name : String, default : => TypeDeclaration) =
            types get name match {
                case Some(t) => t
                case None => insert(default)
            }
    }

    class TopLevelPackage
            extends Package
            with    sc.TopLevelPackage
            with    ScPrintable
    {
        def qualifiedName = AST.QualifiedName("" :: Nil)

        def tryGetAttribute(name : String) : Option[String] = None

        def getName = ""

        def makeScalar(name : String) =
            (types get name).get resolveGenerics Nil

        def functionOf(t : TypesUnbound.Base) =
            (types get "IFunction").get resolveGenerics  t :: Nil

        def observableOf(t : TypesUnbound.Base) =
            (types get "IObservable").get resolveGenerics  t :: Nil

        val EmptyTypeMapper = TypesUnbound.EmptyTypeMapper_Bound

        def genType(name : String) = {
            val scalar  = makeScalar(name)
            val func    = functionOf(scalar)
            val obs     = observableOf(scalar)
            val m = EmptyTypeMapper
            (scalar, scalar bind m, func bind m, obs bind m)
        }

        lazy val (unbound_float,     float_, floatFunc, floatObservable) = genType("Float")
        lazy val (unbound_string,    string_, stringFunc, stringObservable) = genType("String")
        lazy val (unbound_int,       int_, intFunc, intObservable) = genType("Int")
        lazy val (unbound_side,      side_, sideFunc, sideObservable) = genType("Side")
        lazy val (unbound_boolean,   boolean_, booleanFunc, booleanObservable) = genType("Boolean")
    }

    private var topLevelInstance : Option[TopLevelPackage] = None

    def topLevel = topLevelInstance.get

    def withNewTopLevel[T](f : => T) : T ={
        val old = topLevelInstance
        topLevelInstance = Some(new TopLevelPackage)
        val ret = f
        topLevelInstance = old
        ret
    }

    abstract class SubPackageBase extends Package
    {
        def parent : Package

        override def getFunction(name : String) =
            getFunctionImpl(name) match {
                case Some(f) => Some(f)
                case None    => parent getFunction name
            }

    }

    class AnonymousPackage(val parent : Package, override val attributes : Attributes)
            extends SubPackageBase
            with    sc.AnonymousPackage
            with    ScPrintable
    {
        override def qualifiedName = parent.qualifiedName

        def getName = ""

        override def tryGetAttribute(name : String) = attributes.items get name match {
            case Some(v) => Some(v)
            case None    => parent tryGetAttribute name
        }

    }

    class SubPackage(val name   : String,
                     parent     : Package,
                     attributes : Attributes)
            extends AnonymousPackage(parent, attributes)
            with    sc.SubPackage
            with    ScPrintable
    {
        override def qualifiedName = AST.QualifiedName(parent.qualifiedName.names :+ name)

        override def getName = name

        override def equals(o : Any) = o match {
            case that : SubPackage => super.equals(o) && name == that.name
            case _ => false
        }
    }

    trait AnnotationHandler
    {
        val name : String
    }

    object Annotations
    {
        var registry = Map[String, AnnotationHandler]()

        def register(handler : AnnotationHandler){
            registry = registry.updated(handler.name, handler)
        }

        def lookup(name : String) = registry.get(name) match {
            case Some(handler) => handler
            case None => throw new Exception(s"Cannot find annotation handler $name")
        }

        override def toString = registry.toString()
    }

    trait BeforeTyping extends Typed.AnnotationHandler
    {
        def beforeTyping(/** arguments of the annotation     */ args  : List[String])
                        (/** function to process             */ f     : AST.FunDef,
                         /** scope where function is defined */ scope : NameTable.Scope)
    }

    object BeforeTyping
    {
        def apply(scope : NameTable.Scope)
        {
            scope.packages.values foreach { apply }
            scope.anonymous       foreach { apply }

            scope.members.values collect { case f : AST.FunDef =>
                Typer.annotationsOf(f) collect { case Typed.Annotation(g : BeforeTyping, args) => g.beforeTyping(args)(f, scope) }
            }
        }
    }

    trait AfterTyping extends AnnotationHandler
    {
        def afterTyping(/** arguments of the annotation */ args  : List[String])
                       (/** function to process         */ f     : Typed.Function)
    }

    object AfterTyping
    {
        def apply(pkg : Package = topLevel)
        {
            pkg.packages.values foreach { apply(_) }
            pkg.anonymous       foreach { apply(_) }

            pkg.functions.values foreach { f=>
                f.annotations collect { case Typed.Annotation(g : AfterTyping, args) => g.afterTyping(args)(f) }
            }
        }
    }
}

