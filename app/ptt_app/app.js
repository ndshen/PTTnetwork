var express = require('express');
var app = express();

// var apiController = require('./controllers/apiController');
var htmlController = require('./controllers/htmlController');

var port = process.env.PORT || 8888;


app.use('/assets', express.static(__dirname + '/assets'));
app.use('/data', express.static(__dirname + '/data'));

app.set('view engine', 'ejs');

app.use('/', function(req, res, next){
    console.log('Request URL: ' + req.url);
    next();
});

htmlController(app);
// apiController(app);

app.listen(port);