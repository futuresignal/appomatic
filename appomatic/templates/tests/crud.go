func Test_{{submodule}}(t *testing.T){
	log.Println("====================== TEST {{submodule}} ========================")

	//setup our vars here
	{% for k in default_types %}
	{{k}}
	{%endfor%}
	{% for k in new_types %}
	{{k}}
	{%endfor%}

	item := {{module}}.{{struct_name}}{
		{% for col in model['columns'] %}
		{% if col['value'] %}
		{{col['struct_var']}}:{{col['value']}},
		{% endif %}
		{% endfor %}
	}

	//POST
	PerformRequestAndDecode(
    	"{{route}}",
    	"POST",
    	item,
    	nil, 
    	t,
    	&item)

	get_item := {{module}}.{{struct_name}}{}

	//GET
	PerformRequestAndDecode(
    	"{{route}}"+strconv.FormatInt(*item.Id, 10)+"/",
    	"GET",
    	nil,
    	nil, 
    	t,
    	&get_item)

	if !reflect.DeepEqual(get_item, item) {
		t.Errorf("{{submodule}}() get_item = %v, want %v", get_item, item)
	}

	//PUT
	put_item := {{module}}.{{struct_name}}{
		{% for col in model['columns'] %}
		{% if col['put_value'] %}
		{{col['struct_var']}}:{{col['put_value']}},
		{% endif %}
		{% endfor %}
	}
	put_item.Id = item.Id

	put_returned_item := {{module}}.{{struct_name}}{}
	PerformRequestAndDecode(
    	"{{route}}"+strconv.FormatInt(*item.Id, 10)+"/",
    	"GET",
    	put_item,
    	nil, 
    	t,
    	&put_returned_item)

	if !reflect.DeepEqual(put_item, put_returned_item) {
		t.Errorf("{{submodule}}() put_item = %v, want %v", put_item, put_returned_item)
	}

	//DELETE
	del_item := {{module}}.{{struct_name}}{}
	PerformRequestAndDecode(
    	"{{route}}"+strconv.FormatInt(*item.Id, 10)+"/",
    	"DELETE",
    	put_item,
    	nil, 
    	t,
    	&del_item)

	//CHECK THAT DELETE WAS SUCCESSFUL
	res := map[string]interface{}{}
	PerformRequestAndDecode(
    	"{{route}}"+strconv.FormatInt(*item.Id, 10)+"/",
    	"GET",
    	nil,
    	nil, 
    	t,
    	&res)

	//todo: check for delete here

}



