/* Main App
* ====================== */

var App = {

    init: function() {

        this.RegisterPartials()
        this.RegisterHelpers()

        var ServerDropDown = new ServerList({            
            el : $("#server-list")
          , model : new ServerListModel()
        })

        var infoWidget = new InfoWidget({            
            el : $("#info-widget-placeholder")
          , model : new InfoWidgetModel()
        })

        var commandsWidget = new CommandsWidget({            
            el : $("#commands-widget-placeholder")
          , model : new CommandsWidgetModel()
        }) 
        var statusWidget = new StatusWidget({            
            el : $("#status-widget-placeholder")
          , model : new StatusWidgetModel()
        }) 
       
    }

  , RegisterPartials : function(){

      // Handlebars.registerPartial("date-dropdown", $("#date-dropdown-template").html());

  } 

  , RegisterHelpers : function(){

    Handlebars.registerHelper('hash', function ( context, options ) {
  
              var ret = ""
                , counter = 0

              $.each(context, function ( key, value ) {
                
                if (typeof value != "object") {
                  obj = { "key" : key, "value" : value , "index" : counter++ }
                  ret = ret + options.fn(obj)
                }

              })

              return ret
    })

  }
}
