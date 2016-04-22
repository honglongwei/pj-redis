var ServerList = Backbone.View.extend({

  initialize : function() {       
    this.$el.empty()
    this.model.on("change", this.render, this)    
    this.$el.on("change", this.ServerChanged)
    this.model.fetch()   
  }

, ServerChanged : function(){
    $(document).trigger("ServerChange", $(this).val())   
}

, render : function() {
    var model = this.model.toJSON()   
      , self = this  

    $.each(model.servers,function(index, obj){
      self.$el.append("<option value='" + obj.id + "'>" +obj.group+'('+obj.instance+')'+'['+ obj.id +']'+ "</option>")
    })
    var to=self.getQueryString('uri');
    if(to!=null && to.toString().indexOf(':')>0)
    	self.$el.find('option[value="'+to+'"]').attr('selected',true);
    
    self.$el.trigger("change")
  },
  getQueryString: function(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
    }
})