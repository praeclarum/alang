%{
%}

%union {
	int int_val;
	int name;
}

%token <int_val> INT_LITERAL
%token <name> NAME


%left '='
%left '-' '+'
%left '*' '@' '/'
%right NEGATE
%right '^'

%left INDENT
%left DEDENT

%token EOL

%start stmts

%%

stmts
    : stmt
    | stmts EOL stmt
    ;

stmt
    : define
    | expr
    ;

define
    : NAME '=' expr
    | NAME '_' '=' expr
    | NAME '(' ')' '='
    | NAME '(' ')' '=' stmt
    | NAME '(' ')' '=' stmt INDENT stmts DEDENT
    | NAME '(' named_exprs ')' '='
    | NAME '(' named_exprs ')' '=' stmt
    | NAME '(' named_exprs ')' '=' stmt INDENT stmts DEDENT
    ;

expr
    : INT_LITERAL
    | NAME
    | NAME '(' named_exprs ')'
    | NAME '[' named_exprs ']'
    | expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    | '-' expr  %prec NEGATE
    | expr '^' expr
    | '(' named_exprs ')'
    | '{' named_exprs '}'
    ;

named_exprs
    : named_expr_i
    | named_expr_i ','
    ;

named_expr_i
    : named_expr
    | named_expr_i ',' named_expr
    ;

named_expr
    : expr
    ;

%%
