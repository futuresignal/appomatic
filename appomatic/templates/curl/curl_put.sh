
#put {{submodule}}
curl -v -i -H "Content-Type: application/json" -X PUT -d '{{json}}' /api/{{config['api_version']}}/{{submodule}}/{id:[0-9]+}/
#put {{submodule}} with credentials
curl -v -u username:password -i -H "Content-Type: application/json" -X PUT -d '{{json}}' /api/{{config['api_version']}}/{{submodule}}/{id:[0-9]+}/