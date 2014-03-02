var fs = require('fs');
var zerorpc = require("zerorpc");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

client.invoke("hello", "World!", function(error, res, more) {
	console.log(res);
});

var express = require("express");
var app = express();

var port = 3700;

// static server
app.use(express.static(__dirname + '/public'));

// socket.io setup
var io = require('socket.io').listen(app.listen(port));

// jade settings
app.set('views', __dirname + '/templates');
app.set('view engine', "jade");
app.engine('jade', require('jade').__express);
app.get("/", function(req, res){
	res.render("index");
});

app.post("/analyze", function(req, res) {
	var data = new Buffer('');

	req.on('data', function(chunk) {
		data = Buffer.concat([data, chunk]);
	});

	req.on('end', function() {
		req.rawBody = data;

		fs.writeFile("/tmp/test.jpg", data, function(err) {
			if(err) {
				console.log(err);
			} else {
				console.log("The file was saved!");
			}
		}); 

		res.writeHead(200, "OK", {'Content-Type': 'text/html'});
		console.log("OK");
		res.end();
	});
});
 
io.sockets.on('connection', function (socket) {
	socket.emit('message', { message: 'server: hello there' });

	socket.on('send', function (data) {
		io.sockets.emit('message', data);
	});
});
 
console.log("Listening on port " + port);
