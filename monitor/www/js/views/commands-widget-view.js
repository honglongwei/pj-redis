var CommandsWidget = BaseWidget.extend({

    initialize : function() {

      this.Name = "Commands Widget"

      this.init()      
      
      // templates
      var templateSelector = "#commands-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())
      // chart  0
      this.chart0 = new google.visualization.LineChart($("#memory-widget-chart").empty().get(0))
      this.dataTable0 = new google.visualization.DataTable()
      this.dataTable0.addColumn('datetime', 'datetime')
      this.dataTable0.addColumn('number', 'Peak')
      this.dataTable0.addColumn('number', 'Current')   
      
      // chart 1
      this.chart = new google.visualization.AreaChart($("#commands-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable()
      this.dataTable.addColumn('datetime', 'datetime')
      this.dataTable.addColumn('number', 'Commands Processed')   
      
      // chart 2
      this.chart2 = new google.visualization.AreaChart($("#hitrate-widget-chart").empty().get(0))
      this.dataTable2 = new google.visualization.DataTable()
      this.dataTable2.addColumn('datetime', 'datetime')
      this.dataTable2.addColumn('number', 'Hit Rate')   
      //chart 3
      this.chart3 = new google.visualization.LineChart($("#keyspace-widget-chart").empty().get(0))
      this.dataTable3 = new google.visualization.DataTable()
      this.dataTable3.addColumn('datetime', 'datetime')
      this.dataTable3.addColumn('number', 'persists')
      this.dataTable3.addColumn('number', 'expires')  
     //chart 4
      this.chart4 = new google.visualization.LineChart($("#kick-widget-chart").empty().get(0))
      this.dataTable4 = new google.visualization.DataTable()
      this.dataTable4.addColumn('datetime', 'datetime')
      this.dataTable4.addColumn('number', 'expired')
      this.dataTable4.addColumn('number', 'evicted')  
    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      self.dataTable0.removeRows(0,self.dataTable0.getNumberOfRows())
      self.dataTable.removeRows(0,self.dataTable.getNumberOfRows())
      self.dataTable2.removeRows(0,self.dataTable2.getNumberOfRows())
      self.dataTable3.removeRows(0,self.dataTable3.getNumberOfRows())
      self.dataTable4.removeRows(0,self.dataTable4.getNumberOfRows())
            
      $.each(model.data, function(index, obj){          
          
          // first item of the object contains datetime info
          // [ YYYY, MM, DD, HH, MM, SS ]
          var recordDate = new Date(obj[0][0], obj[0][1]-1, obj[0][2], obj[0][3], obj[0][4], obj[0][5])
          if(self.dataTable0)
              self.dataTable0.addRow( [recordDate, obj[7],obj[8]] )
          if(self.dataTable)
            self.dataTable.addRow( [recordDate, obj[1]] )
          if(self.dataTable2)
            self.dataTable2.addRow( [recordDate, obj[6]] )	
          if(self.dataTable3)
            self.dataTable3.addRow( [recordDate, obj[3],obj[2]] )	
          if(self.dataTable4)
            self.dataTable4.addRow( [recordDate, obj[4],obj[5]] )	
      })
     
      var pointSize = model.data.length > 120 ? 1 : 5
        , options = {
                      title : ''
                    , colors: [ '#17BECF', '#9EDAE5' ]
                    , areaOpacity : .9                    
                    , pointSize: pointSize                      
                    , chartArea: { 'top' : 10, 'width' : '85%' }
                    , width : "100%"
                    , height : 200
                    , animation : { duration : 500, easing: 'out' } 
                    , vAxis: { minValue : 0 }
                    }
      ,options2 = {
              title : ''
                  , colors: [ '#1581AA', '#77BA44' ]                    
                  , pointSize: pointSize 
                  , chartArea: { 'top' : 10, 'width' : '85%' }
                  , width : "100%"
                  , height : 200
                  , animation : { duration : 500, easing : 'out' }                    
                  }
      if($(this.chart0.cd).parent().css("display") !="none")
      this.chart0.draw(this.dataTable0, options2)
      
      if($(this.chart.cd).parent().css("display") !="none")
      this.chart.draw(this.dataTable, options2)
      
      if($(this.chart2.cd).parent().css("display") !="none")
      this.chart2.draw(this.dataTable2, options2)
      
      if($(this.chart3.cd).parent().css("display") !="none")
      this.chart3.draw(this.dataTable3, options2)
      
      if($(this.chart4.cd).parent().css("display") !="none")
      this.chart4.draw(this.dataTable4, options2)
      
      if($('#cb_slowlog').attr("checked")=="checked"){
      		$('#cb_slowlog').trigger('click');
      		$('#cb_slowlog').attr('checked','checked');
      	}
    }
})