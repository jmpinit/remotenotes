var fs = require('fs');
var zerorpc = require("zerorpc");
var uuid = require('node-uuid');

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

var express = require("express");
var app = express();

var port = 3700;

// static server
app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/data'));

// socket.io setup
var io = require('socket.io').listen(app.listen(port));

var notes = [];

// jade settings
app.set('views', __dirname + '/templates');
app.set('view engine', "jade");
app.engine('jade', require('jade').__express);

app.post("/analyze", function(req, res) {
	var data = new Buffer('');

	req.on('data', function(chunk) {
		data = Buffer.concat([data, chunk]);
	});

	req.on('end', function() {
		req.rawBody = data;

		// generate a new id for this picture
		var id_pic = uuid.v4();
		var fn_pic = __dirname + "/data/image/" + id_pic + ".jpg";

		fs.writeFile(fn_pic, data, function(err) {
			if(err) {
				console.log(err);
			} else {
				notes.push(id_pic);
				io.sockets.emit('notes', { message: notes });

				console.log(id_pic + " saved.");

				client.invoke("save", fn_pic, function(error, res, more) { });
			}
		}); 

		res.writeHead(200, "OK", {'Content-Type': 'text/html'});
		console.log("OK");
		res.end();
	});
});

app.get("/note/:basename", function(req, res) {
	var basename_pic = req.params.basename;
	var fn_pic = "data/image/" + basename_pic + ".jpg";
	var url_pic = "/image/" + basename_pic + ".jpg";

	console.log("request for image " + url_pic);

	res.render('image', {
		id_pic: basename_pic,
		url_pic: url_pic
	}); 
});

app.get("/", function(req, res) {
	console.log("rendering index");
	console.log(notes);

	res.render('index', {
		notes: notes
	});
});
 
io.sockets.on('connection', function (socket) {
	socket.emit('notes', { message: notes });
});

io.sockets.on('reconnection', function (socket) {
	socket.emit('notes', { message: notes });
});

console.log("Listening on port " + port);
