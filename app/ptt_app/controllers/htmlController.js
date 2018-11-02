var bodyParser = require('body-parser');

var urlencodedParser = bodyParser.urlencoded({ extended: false });

module.exports = function(app){
    // app.get('/', function(req, res){
    //     var adr = req.protocol + "://" + req.get('host');
    //     res.render('index', { link: adr + "/home" });
    // });
    app.get('/', function(req, res){
        var adr = req.protocol + "://" + req.get('host');
        // res.render('index', { home_link: adr + "/home"});
        res.render('home', { demo_link: adr + "/demo" , home_link: adr + "/home"});
    });
    app.get('/home', function(req, res){
        var adr = req.protocol + "://" + req.get('host');
        res.render('home', { demo_link: adr + "/demo" , home_link: adr + "/home"});
    });
    app.get('/demo', function(req, res){
        var adr = req.protocol + "://" + req.get('host');
        res.render('demo', { home_link: adr + "/home" });
    });
    app.get('/group/:id', function(req, res){
        var adr = req.protocol + "://" + req.get('host');
        let id = req.params.id;
        res.render('group', { demo_link: adr + "/demo" , home_link: adr + "/home", id: id });
    });
};