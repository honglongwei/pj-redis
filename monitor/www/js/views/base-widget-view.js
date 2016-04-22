var BaseWidget = Backbone.View.extend({

  enableLogging : false

, updateFrequency : 3000

, Name : "BaseWidget"

, server : ""
/*
, events : {
             "click .time-period" : "ChangeTimeFrame"
           , "click .go" : "Go"          
           }*/

, init : function () {

      var self = this

      $(document).on("ServerChange", function(e, server){   
    	  if(self.server==""){
    		  	self.server = server; 
    		  	//first triggle defalut
    		  	$("#time-period-defalut").click();
    	        //self.UpdateModel(true);
    		}
    	  else if(self.server !=server){
        	  self.server = server;  
        	  self.UpdateModelInner(true,true);
          }       
      })    
      
      $(".time-period").click(function(el){
    	  self.ChangeTimeFrame(self,el);
      });
      $(".go").click(function(el){
    	  self.Go(el);
      });
      // set event listners
      this.model
        .on("error", this.error, this)
        .on("error",this.ModelChanged,this)
        .on("change", this.ModelChanged, this);
      
        this.timer=null;
  },UpdateModel:function(enableTimer) {
	  this.UpdateModelInner(enableTimer, false)
  }
, UpdateModelInner : function ( enableTimer ,onlyOnce) {    
	if(!onlyOnce){
	    this.enableTimer = enableTimer;
		if(this.timer!=null)
	    {
	    	clearTimeout(this.timer) 
	    	this.timer=null
	    }
	}
	
    this.startTime = new Date()
    var vfrom= $(document).find('[name=from]').val();
    var vto =$(document).find('[name=to]').val();
    
    //stop
    if(vfrom.length!=0 || vto.length!=0)
    	this.enableTimer =false;
    
    this.model.fetch({
        data : { 
          from : vfrom
        , to :  vto
        , server : this.server
      }
    })
  }

, ModelChanged : function(){

    this.endTime = new Date()
    var timeElapsed = (this.endTime - this.startTime);
    
    if (this.enableLogging)
      console.log(this.Name + ": Time Elapsed = " + timeElapsed + " ms")

    this.render()

    if(this.enableTimer && this.timer==null)     
    {
      var self = this
      this.timer = setTimeout( function () { self.UpdateModel(true) }, this.updateFrequency )              
    }
} 

, Go : function( el ) {
    this.UpdateModel(false)
  }

, ChangeTimeFrame : function (self, el ) {

    var selectionType = $(el.target).data("type")
      , timeFrame = parseInt( $(el.target).data("time") )
   
    // update the dropdown's label
    $(el.target)
      .closest(".btn-group")
      .children()
      .first()
      .text($(el.target).text())

    // Custom time frame selected
    if ( selectionType == "custom" ) {
      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","inline")      
    }
    // real time    
    else if ( selectionType == "realtime" ) {
      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","none")
      
     
      $(document).find('[name=from]').val("")
      $(document).find('[name=to]').val("")
      self.timer = setTimeout( function () { self.UpdateModel(true) }, this.updateFrequency )      
    }
    // one of the template time frame selected
    // example: last 15mins, last 1 day etc    
    else {

      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","none")      

      var endDate = new Date()
        , startDate = endDate          

      switch(selectionType) {

        case 'minute' : 
          startDate = new Date(endDate - timeFrame * 60000)
          break
                       
        case 'hour' :  
          startDate = new Date(endDate - timeFrame * 60*60000)
          break

        case 'day' :  
          startDate = new Date(endDate - timeFrame * 24*60*60000)
          break

        case 'week' :  
          startDate = new Date(endDate - timeFrame * 7*24*60*60000)
          break

        case 'month' :  
          startDate = new Date(endDate - timeFrame * 30*24*60*60000)
          break
      }
      

      $(document).find('[name=from]').val(self.ISODateString(startDate))
      $(document).find('[name=to]').val(self.ISODateString(endDate))              
      self.UpdateModel(false)
    }
  }

, ISODateString : function ( d ) {

    function pad ( n ) {
      return n < 10 ? '0'+n : n
    }
    
    return d.getFullYear()+'-'
         + pad(d.getMonth()+1)+'-'
         + pad(d.getDate())+' '
         + pad(d.getHours())+':'
         + pad(d.getMinutes())+':'
         + pad(d.getSeconds())
  }

, error: function ( model, error ) {
   if (this.enableLogging)
      console.log(this.Name + ": Error Occured \n" + error + "\n" + model )

  }
        
})