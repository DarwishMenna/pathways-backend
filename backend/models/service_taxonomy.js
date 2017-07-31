var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var ServiceTaxonomySchema = new Schema({
  id:  { type: String, required: true },
  service_id: { type: String, required: true },
  taxonomy_id: { type: String, required: true },
  taxonomy_detail: String
}, { collection : 'service_taxonomy' });

module.exports = mongoose.model('ServiceTaxonomy', ServiceTaxonomySchema );
