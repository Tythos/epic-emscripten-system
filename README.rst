epic-emscripten-system
======================

Build graph and supporting scripts for a self-contained epic-based build of
system libraries from emscripten.

There are three steps:

#. Set EMSCRIPTEN_REPO_PATH to the path where you have cloned the following
   repository:

   https://github.com/emscripten-core/emscripten

#. Choose a specific library build graph; supported build graphics include:

   * The MUSL libc implementation ("build_graph_libc_musl.csv")

   * The libcxx stdlib implementation ("build_graph_stdlib_libcxx.csv")

   * The emscripten system libraries ("build_graph_emscripten_system.csv")

#. Compile, link, and archive that build graph using the local epic script; for
   example, using the "build_graph_libc_musl.csv" build graph:

   > python epic.py compile build_graph_libc_musl.csv

   > python epic.py link build_graph_libc_musl.csv

   > python epic.py archive build_graph_libc_musl.csv

The resulting product should be a static library generated in the "lib/" folder
(git-ignored) located in the directory where this README/repository has been
cloned.
