/* Pandoras Box Automation - JavaScript.NodeJS v{{ version }} @{{ time }} <support@coolux.de> */
var httplib = require('http');{% for et in enums %}
var {{et.name|camelize}}={ {% for e in et['values'] %}{{ e.key|camelize }}: {{ e.val }}{% if loop.last == false %},{% endif %}{% endfor %} };{% endfor %}
function PBAuto(host, port){this.h=host;this.p=port}{% for command in commands %}
PBAuto.prototype.{{ command.name|camelize_small }} = function({% for a in command.send %}{{ a.name|camelize_small }}, {% endfor %}callback){var b = new Buffer();b.writeShort({{command.code}});{% for a in command.send %}b.write{{ types[a.type_id].name|camelize }}({{ a.name }});{% endfor %}this.send(b, callback || false, [{% for r in command.recv %}{name: '{{ r.name|camelize_small }}', type: '{{ types[r.type_id].name|camelize }}'}{% if loop.last == false %}, {% endif %}{% endfor %}]);}{% if loop.last == false %},{% endif %}{% endfor %}
PBAuto.prototype.send = function(t, e, r){
	var rb = Base64.encode(t.getRawBytes());
	var req = httplib.request(
		{host: this.h,port: this.p,path: '/',method: 'PBAUTO',headers: {'User-Agent': 'NodeJS.PBAuto/1.0','Content-Length': rb.length,'Accept': 'text/html','Content-Type': 'text/plain; charset=UTF-8'} },
		function(res)
		{
			var body = '';
            res.setEncoding('utf8');
            if("function" == typeof e)
            {
		        res.on('data', function(d) {body += d;});
            	res.on('end', function()
            		{
	                    var t = {http: res.statusCode,ok: 200 === res.statusCode,code: -1 / 0};
	                    if (t.ok) {
	                        var o = new Parser(Base64.decode(body));
	                        if (t.code = o.readShort(), t.code >= 0)
                        	{
                        		for (var s = 0; s < r.length; s++) t[r[s].name] = o["read" + r[s].type]();
                        	}
                        	else
                        	{
                        		t.ok = false;
                        		t.code = o.readInt();
                        	}
	                    }
	                    else
                    	{
                    		t.ok = false;
                    		console.log("PBAuto Error", req.statusCode);
                    	}
	                    e(t);
                	}
                );
        	}
    	}
    	);
    req.write(Base64.encode(t.getRawBytes()));
    req.end();
}
{% include "javascript-core.js" %}
module.exports = PBAuto