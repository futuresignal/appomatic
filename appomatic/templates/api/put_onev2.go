
//
// PutOne_{{table_name}} Profides our update endpoint
// Only specific rows are updateable (non pk, non fk)
// Params: 
// Returns: 
//
func PutOne_{{table_name}}(w *utils.ResponseWrapper, r *http.Request){
	
	vars := mux.Vars(r)
	id,err := strconv.ParseInt(vars["id_{{table_name}}"], 10, 64)

	if err != nil {
		w.SendResponse(400, map[string]string{"error":"Invalid id"}, err)
		return
	}

	//decode json
	var new_struct {{struct_name}}
	if err = utils.DecodePost(&new_struct, w, r); err != nil {
		w.SendResponse(400, map[string]string{"error":"Not able to decode object"}, err)
		return
	}

	//get the current DB version of this struct by ID
	current_struct,err := ReadOne_{{table_name}}(id)
	if err != nil || current_struct.Id == nil {
		w.SendResponse(500, map[string]string{"error":"Unable to read existing item"}, err)
		return
	}

	//update any fields allowed to be ovewritten
	{% for col in okCols %}
	if new_struct.{{col}} != nil {
		current_struct.{{col}} = new_struct.{{col}}
	}
	{% endfor %}
	
	err = UpdateOne_{{table_name}}(&new_struct)
	if err != nil {
		w.SendResponse(500, map[string]string{"error":"Resource not updated"}, err)
		return
	} 

	w.SendResponse(200, new_struct, err)
	return
	
}

