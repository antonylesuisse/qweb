# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
	include QWebRails
	alias :render_orig :render
	alias :render :qweb_render
	def everytime(); qweb_load end
	before_filter :everytime
end
class MainController < ApplicationController
	def index
		f = $qweb.form("main/index", {}, @request)
		p default_template_name
	end
end
