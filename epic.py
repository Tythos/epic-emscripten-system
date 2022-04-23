"""
Standalone, streamlined/minimal version of EPIC build script for clang-based
WASM builds.
"""

import os
import csv
import sys
import subprocess

EMSCRIPTEN_REPO_PATH = os.getenv("EMSCRIPTEN_REPO_PATH")

class BuildGraph(object):
    """
    """

    def __init__(self, path):
        """
        """
        self.path = path
        with open(path, 'r') as f:
            dr = csv.DictReader(f)
            self.build_graph = [row for row in dr]

    def getEdgesByAction(self, action):
        """
        """
        return [e for e in self.build_graph if e["action"] == action]

    def getVertices(self):
        """
        Returns list of all unique vertices in the graph
        """
        froms = [e["from"] for e in self.build_graph]
        tos = [e["to"] for e in self.build_graph]
        return list(set(froms + tos))

    def getSourceVertices(self):
        """
        Returns list of all vertices that do not have predecessors
        """
        sources = []
        vertices = self.getVertices()
        for v in vertices:
            froms = [e for e in self.build_graph if e["from"] == v]
            if len(froms) == 0:
                sources.append(v)
        return list(set(sources))

    def getIntermediateVertices(self):
        """
        Returns a list of all intermediate vertices (build products), as
        determined by those with both "to" and "from edge connections.
        """
        intermediates = []
        vertices = self.getVertices()
        for v in vertices:
            froms = [e for e in self.build_graph if e["from"] == v]
            tos = [e for e in self.build_graph if e["to"] == v]
            if 0 < len(tos) and 0 < len(froms):
                intermediates.append(v)
        return list(set(intermediates))

    def getFinalVertices(self):
        """
        Analyzes edges to determine which vertices are listed only as "to".
        """
        finals = []
        vertices = self.getVertices()
        for v in vertices:
            froms = [e for e in self.build_graph if e["from"] == v]
            tos = [e for e in self.build_graph if e["to"] == v]
            if len(froms) == 0 and 0 < len(tos):
                finals.append(v)
        return list(set(finals))

    def getEdgesFrom(self, fromVertex):
        """
        Returns the operations (edges) generated from the given "from" vertex
        """
        return [e for e in self.build_graph if e["from"] == fromVertex]

    def getEdgesTo(self, toVertex):
        """
        Returns the operations (edges) that generate the given to (vertex).
        """
        return [e for e in self.build_graph if e["to"] == toVertex]

class Actor(object):
    @classmethod
    def run(Cls, args):
        """
        """
        sp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = sp.communicate()
        if 0 < sp.returncode:
            print(" > %s" % " ".join(args))
            raise Exception("%s actor failed" % Cls.__name__)

class LlvmWasmActors(Actor):
    """
    """
    LLVM_ROOT = "C:\\Program Files\\LLVM\\bin"
    WASMOPT = ""
    DBGCFLAGS = ["-DNDEBUG"]
    SYS_CCFLAGS = ["-Ofast", "-std=gnu99", "-fno-threadsafe-statics"] + \
        ["-DNDEBUG", "-Dunix", "-D__unix", "-D__unix__"] + \
        ['-isystem"%s/system/lib/libc/musl/src/internal"' % EMSCRIPTEN_REPO_PATH] + \
        ["-Wno-dangling-else", "-Wno-ignored-attributes", "-Wno-bitwise-op-parentheses", "-Wno-logical-op-parentheses", "-Wno-shift-op-parentheses", "-Wno-string-plus-int"] + \
        ["-Wno-unknown-pragmas", "-Wno-shift-count-overflow", "-Wno-return-type", "-Wno-macro-redefined", "-Wno-unused-result", "-Wno-pointer-sign"]
    CLANGFLAGS = ["-target", "wasm32", "-nostdinc"] + \
        ["-D__EMSCRIPTEN__", "-D_LIBCPP_ABI_VERSION=2"] + \
        ["-fvisibility=hidden", "-fno-builtin", "-fno-exceptions", "-fno-threadsafe-statics"] + \
        ['-isystem"%s/include/libcxx"' % EMSCRIPTEN_REPO_PATH] + \
        ['-isystem"%s/include/compat"' % EMSCRIPTEN_REPO_PATH] + \
        ['-isystem"%s/include"' % EMSCRIPTEN_REPO_PATH] + \
        ['-isystem"%s/include/libc"' % EMSCRIPTEN_REPO_PATH] + \
        ['-isystem"%s/lib/libc/musl/arch/emscripten"' % EMSCRIPTEN_REPO_PATH]
    LDFLAGS = ["-strip-all", "-gc-sections"] + \
        ["-no-entry", "-allow-undefined", "-import-memory"] + \
        ["-export=__wasm_call_ctors", "-export=malloc", "-export=free", "-export=main"] + \
        ["-export=square"]

class Clang(LlvmWasmActors):
    @classmethod
    def execute(Cls, fromVertex, toVertex):
        """
        """
        exePath = os.path.abspath("%s\\clang.exe" % Cls.LLVM_ROOT)
        Cls.run([exePath] +
            Cls.SYS_CCFLAGS +
            Cls.CLANGFLAGS +
            ["-o", toVertex, "-c", fromVertex])

def help():
    """
    """
    print(main.__doc__)

def compile(bg):
    """
    """
    actor = Clang()
    for e in bg.getEdgesByAction("compile"):
        print("Compiling '%s' into '%s'..." % (e["from"], e["to"]))
        actor.execute(e["from"], e["to"])

def link(bg):
    """
    """
    pass

def optimize(bg):
    """
    """
    pass

def archive(bg):
    """
    """
    pass

def clean(bg):
    """
    """
    for e in bg.getIntermediateVertices():
        if os.path.isfile(e):
            os.unlink(e)
    for e in bg.getFinalVertices():
        if os.path.isfile(e):
            os.unlink(e)

def main(script, action, path=None):
    """
    Command line invocation is a two-argument structure indicating action and path:

    > python epic.py {action} {path}

    Supported actions include:
    * "help": prints this markup
    * "compile": invokes compiler actor on relevant segments of the build graph
    * "link": invokes linker actor on relevant segments of the build graph
    * "optimize": invokes optimizer actor on relevant segments of the build graph
    * "archive": invokes archive actor on relevant segments of the build graph
    * "clean": removes all intermediate and final build artifacts

    The "path" argument should reference a build graph table, .CSV formatted,
    in which each row defines a specific transformation with the following
    columns:
    * "from": source file for the given transformation
    * "action": one of the following: "compile", "link", "archive"
    * "to": destination file for the given transformation

    For example, the following CSV indicates the file "main.c" is compiled into
    the object file "main.o":

      from,action,to
      main.c,compile,main.o

    For example, to perform all "compile" transforms against a build graph in
    the current folder, you would invoke:

    > python epic.py compile ./build_graph.csv
    """
    if action == "help":
        help()
    elif action == "compile":
        compile(BuildGraph(path))
    elif action == "link":
        link(BuildGraph(path))
    elif action == "optimize":
        optimize(BuildGraph(path))
    elif action == "archive":
        archive(BuildGraph(path))
    elif action == "clean":
        clean(BuildGraph(path))
    else:
        raise Exception("Unsupported action '%s'" % action)

if __name__ == "__main__":
    #main(*sys.argv)
    main(None, "compile", "build_graph_libc_musl.csv")
