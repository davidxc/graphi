                               Graphi


	- What is Graphi?

	   Graphi is a web application for drawing directed graphs from the output of profilers.
           Each node in the graph represents a function and is labeled with the function's name
           and percentage running time. An edge represents a call from a function to another function.

           Graphi also creates a sortable table of function calls and running times.

        - What libraries does Graphi depend on?

	   Graphi depends on liviz.js, jQuery > 1.8, jQuery forms plugin, jQuery dataTables
           plugin, Django > 1.4, and gprof2dot. 

	   Liviz.js, jQuery, jQuery forms plugin, and jQuery dataTables plugin are included in this
           repository. You only need to install Django and gprof2dot. Both of these can be installed with pip.


	- Is there a help page?

	  Please see the FAQ template in the /graphi/graphi_project/graphi_project/templates folder. You can also
          email me at davidwong.xc@gmail.com.

       
