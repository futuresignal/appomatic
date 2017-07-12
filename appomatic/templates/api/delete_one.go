
//
// DeleteOne_{{table_name}} Profides our delete endpoint
// Soft deletes this item
// Params: id int64
// Returns: id of item deleted
//
func DeleteOne_{{table_name}}(w *utils.ResponseWrapper, r *http.Request){
	
	vars := mux.Vars(r)
	
	id,err := strconv.ParseInt(vars["id_{{table_name}}"], 10, 64)
	if err != nil {
		w.SendResponse(400, map[string]string{"error":"Invalid id"}, err)
		return
	}

	err = DelOne_{{table_name}}(id)
	if err != nil {
		w.SendResponse(500, map[string]string{"error":"Internal error"}, err)
		return
	} 

	w.SendResponse(200, map[string]string{"result":"successfully deleted {{table_name}} id "+vars["{{table_name}}_id"]}, err)
	return
}

