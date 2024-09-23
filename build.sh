

GRAMMAR="interaction"
START="interaction"

ANTLR=`which antlr`
MISSING=`which antlr | egrep "not found"`

if [ -n "$MISSING" ]; then
    echo "ANTLR runtime is missing, please install runtime. e.g. brew install antlr"
    exit
fi

export CLASSPATH=".:$ANTLRJAR"

echo "Creating Python recognizer in gen-python"
antlr -o gen-python -listener -Dlanguage=Python3 -no-visitor -lib . $GRAMMAR.g4

echo "Creating Java recognizer in gen-java"
antlr -o gen-java -listener -Dlanguage=Java -no-visitor -lib . $GRAMMAR.g4

echo "Compiling Java tools for grammar $GRAMMAR in gen-java"
cd gen-java;

export CLASSPATH="/usr/local/Cellar/antlr/4.9.3/antlr-4.9.3-complete.jar:."
javac $GRAMMAR*.java


#TODO: build test harness
#echo "Testing grammar"
#echo "Test input:" 
#cat ../examples/test1
#echo "Results:"
#grun $GRAMMAR $START ../examples/test1 -tree

