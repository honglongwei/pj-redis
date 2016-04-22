/* Status Widget
* ====================== */

var StatusWidget = BaseWidget.extend({

  initialize : function() {  

    this.Name = "Status Widget"

    this.init()
    this.updateFrequency = 5000 // every 5 seconds
        
    // templates
    var templateSource        = $("#status-widget-template").html()
    this.template         = Handlebars.compile(templateSource)
  }
  
, render: function() {

    var model         = this.model.toJSON()
      , markUp        = this.template(model.data)

    $(this.el).html(markUp)
}
})