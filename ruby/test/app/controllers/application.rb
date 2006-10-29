# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
    # called on every request
    def everytime()
    end
    before_filter :everytime

	# overide the default render
    def qweb_render(template=nil)
        fname=File.dirname(__FILE__)+"/demo.xml"
        if File.mtime(fname).to_i!=$qweb_time
            $qweb=QWebHTML.new(fname)
            $qweb_time=File.mtime(fname).to_i
        end
        add_variables_to_assigns
        template ||= default_template_name
        if $qweb.template_exists?(template)
            render_text($qweb.render(template,@assigns))
        else
            return false
        end
    end
    alias :render_rail :render
    def render(arg=nil)
        t=nil
        t=arg[:template] if arg.kind_of?(Hash)
        r=qweb_render(t)
        return render_rail(arg) unless r
    end

	#q=QWebHTML.new("demo.xml")
	#f = q.form("form",@request, v, "user")
end
class MainController < ApplicationController
	def index
		$qweb.form()
#		render_text "caca"
	end
end
