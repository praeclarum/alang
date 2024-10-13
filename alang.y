%{
    int yylex(void);
    void yyerror(char const *);
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

%token EOL

%start stmt_list

%%

stmt_list
    : stmt
    | stmt_list EOL stmt
    ;

stmt
    : expr
    | set
    ;

set
    : NAME '=' expr
    | NAME '_' '=' expr
    | NAME parameters '=' expr
    ;

expr
    : INT_LITERAL
    | NAME
    | NAME '(' arguments ')'
    | expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    | '-' expr  %prec NEGATE
    | expr '^' expr
    | '(' expr ')'
    ;

arguments
    : argument
    | arguments ',' argument
    ;

argument
    : expr
    ;

parameters
    : parameter
    | parameters ',' parameter
    ;

parameter
    : NAME ':' type
    | NAME
    ;

type
    : NAME
    ;

%%
