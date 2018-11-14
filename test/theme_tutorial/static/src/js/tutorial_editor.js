(function() {
   'use strict';
   var website = odoo.website;
   website.odoo_website = {};
   website.snippet.options.snippet_testimonial_options = website.snippet.OPTIONS.extend({
       onFocus: function() {
           alert("On focus!");
       }
   })
})();