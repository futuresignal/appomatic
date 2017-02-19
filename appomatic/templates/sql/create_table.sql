CREATE TABLE "{{table_name}}" (
{% for col in cols %}
"{{col['title']}}" {{col['db_type']}},
{% endfor %}
PRIMARY KEY ("id")
);
COMMENT ON TABLE "{{table_name}}" IS '{{comment}}';