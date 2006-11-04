# Filters added to this controller will be run for all controllers in the application.
# Likewise, all the methods added will be available for all controllers.
require "qweb"

class ApplicationController < ActionController::Base
	alias :render_orig :render
	include QWebRails
	def everytime(); qweb_load end
	before_filter :everytime
end
class MainController < ApplicationController
	def index
		p default_template_name
	end
end
