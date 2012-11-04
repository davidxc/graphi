/*
 -> JSViz <-
 Interactive GraphViz on DHTML

-- MIT License

Copyright (c) 2011-2012 Satoshi Ueyama

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/

(function() {
	function setWorkerSTDIN(txt) {
		postArgMessage(dotWorker, "setWorkerSTDIN", txt); }
	function setupGVContext(opt) {
		postArgMessage(dotWorker, "setupGVContext", opt); }
	function runDotLayout() {
		postArgMessage(dotWorker, "runDotLayout"); }

	var dotWorker = null;
	var progressView = null;
	var graphsCtrl = null;
	var stopGo = null;
	var startAnimationFunc = null;
	var appScreen = null;
	var errorSink;
	var demoDiffPager = null;
	
	var runOptions = {
		slow: false,
		prog: false
	};

		
	
	function create_nodes(nodes) {
		nodes_set = "{node[shape=box] ";
		for (var i=0; i < nodes.length; i++) {
			nodes_set = nodes_set + '"' + nodes[i]['label'] + '"'  + ';';
		}
		nodes_set = nodes_set + ' }';
		return nodes_set;
	}
	
	function create_edges(edges) {
		edges_set = "{ "
		for (var i=0; i < edges.length; i++) {
			edge_template = 'edge[label="edge_label"] "start" -> "end"; ';
			edge_template = edge_template.replace('edge_label', edges[i]['label']);
			edge_template = edge_template.replace('start', edges[i]['start']);
			edge_template = edge_template.replace('end', edges[i]['end']);
			edge_template = edges_set = edges_set + edge_template;
		}
		edges_set = edges_set + " }"
		return edges_set;
	}
	
	function createTable(nodes) {
		// Creates table of function calls and running times.
		
		for (var i=0; i < nodes.length; i++) {
			var row = $('<tr>');
			elements = nodes[i]['label'].split('\\n');
			for (var j=0; j < elements.length; j++) {
				row_cell = '<td>' + elements[j] + '</td>';
				$(row_cell).appendTo(row);
			}
			$('#profile_table_body').append(row);
		}
	}
	
	function insertData_postForm(json, status) {
		nodes = create_nodes(json["nodes"]);
		edges = create_edges(json["edges"]);
		graph = "digraph { ranksep=0.2; node [height=0.375]; "
		graph = graph + nodes + " " + edges + " " + "}";
		$('#dot-src').html(graph);
		startDot();
		runDotLayout();
		createTable(json["table_nodes"]);
		$('#profile_table').dataTable();
		$('#profile_table').css('left', '0px');
		$('#profile_table').css('top', '0px');
	}
	
    
	
	window.w_launch = function() {
		$('#profileform').on('submit', function(e) {
			e.preventDefault();
			$(this).ajaxSubmit({
				success: insertData_postForm
			})
		});
		setupUI();
		graphsCtrl = new JSViz.GraphsController('graph-svg');
		appScreen.watchResize(graphsCtrl, document.body, true);
		appScreen.goButton.setEnabled(false);
		appScreen.goButton.onOptionalCommand = onOptionalMenuCommand;
		
		dotWorker = new Worker("/static/worker-main.js?v=2");
		setupMessageHandler(dotWorker);
		stopGo = new WorkerStopGo.Controller(dotWorker,
			function(){ // stopGo ready
				postArgMessage(dotWorker, "init");
			},
			function() { // worker task complete
			
			});
		
		appScreen.goButton.setEnabled(true);
		runOptions.slow = false;
		runOptions.prog = false;
		// startDot and runDotLayout have been moved into insertData(json)
		// startDot();
		// runDotLayout();
		$.ajax({
			url: "/parsepython-example/",
			success: insertData_postForm,
		});
	};
	
	
	function afterInit() {
		appScreen.goButton.setEnabled(true);
		
		appScreen.goButton.eventDispatcher().click(function(){
			runOptions.slow = false;
			runOptions.prog = false;
			startDot();
		});
	}
	
	function onOptionalMenuCommand(cmd) {
		switch(cmd) {
		case 'cmd-prog':
			runOptions.slow = false;
			runOptions.prog = true;
			startDot();
			break;
		case 'cmd-slow':
			runOptions.slow = true;
			runOptions.prog = false;
			startDot();
			break;
		case 'cmd-demo':
			demoDiffPager = new difftype.DiffPager("./demodata", appScreen.codingTextBox, function() {
				runOptions.slow = demoDiffPager.currentPageData.slow;
				runOptions.prog = demoDiffPager.currentPageData.prog;
				startDot();
				
			});
			
			break;
		case 'cmd-about':
			window.open('./about/');
			break;
		}
	}
	
	function startDot() {
		var btn = appScreen.goButton;
		if (!btn.enabled) { return; }
		
		btn.setEnabled(false);
		setWorkerSTDIN( document.getElementById('dot-src').value );
		setupGVContext(runOptions);
	}

	function afterErrorCheck(param) {
		errorSink.load(param);
	}

	function nextReady() {
		appScreen.goButton.setEnabled(true);

		if (demoDiffPager) {
			if (!demoDiffPager.next()) {
				demoDiffPager = null;
				appScreen.codingTextBox.style.fontSize = '';
			}
		}
	}
	
	function afterSetupGVContext(param) {
		appScreen.errorIndicator.update();
		if (errorSink.countFatal() < 1) {
			stopGo.run();
		} else {
			nextReady();
		}
	}
	
	
	function afterRunDotLayout(param) {
		var extractor = new JSViz.GraphExtractor();
		var graphInfo;
		if (param[0].type == "G") {
			graphInfo = param.shift();
		}
		
		extractor.extractFromJSON(param);
		graphsCtrl.setDisplayGraphSize(extractor.g, graphInfo.displayWidth, graphInfo.displayHeight);
		startAnimationFunc = function() {
			graphsCtrl.setNewGraph(extractor.g, runOptions.slow, function(){
				nextReady();
			});
		};
		
		if (!runOptions.prog) {
			startAnimationFunc();
		}
	}

	function setupUI() {
		errorSink = new JSViz.ErrorSink();
		appScreen = new JSViz.AppScreen({
			codingAreaContainer: "coding-area",
			codingTextBox:       "dot-src",
			menuBox:             "dot-options"
		});
		
		appScreen.setupErrorIndicator(errorSink);
	}

	function recvProgress(j) {
		var pg = JSViz.ProgressModel.fromJSON(j);
		if (pg.state == PROGRESS_LAYOUT_FINISH) {
			progressView.hideWithAnimation();
			startAnimationFunc();
		} else {
			progressView.setNext(pg);
			progressView.startAnimation();
		}
	}
	
	function setupMessageHandler(wk) {
		wk.addEventListener("message", function(event){
			var etype  = event.data.type;
			var arg0   = event.data.arg0 || null;
			
			switch(etype) {
			case "afterInit":
				afterInit(); break;
				
			case "afterSetupGVContext":
				afterSetupGVContext(JSON.parse(arg0)); break;
			case "afterRunDotLayout":
				afterRunDotLayout(JSON.parse(arg0)); break;
			case "afterErrorCheck":
				afterErrorCheck(JSON.parse(arg0)); break;
			case "sendProgress":
				recvProgress(JSON.parse(arg0)); break;
			case "log":
				console.log(arg0); break;
			}
		});
	}
})();
