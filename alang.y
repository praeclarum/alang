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
%left '*' '/'
%left NEG
%right '^'

%start expr

%%

expr
    : INT_LITERAL
    | NAME
    | NAME '=' expr
    | NAME '(' expr ')'
    | expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    | '-' expr  %prec NEG
    | expr '^' expr
    | '(' expr ')'
    ;

%%
