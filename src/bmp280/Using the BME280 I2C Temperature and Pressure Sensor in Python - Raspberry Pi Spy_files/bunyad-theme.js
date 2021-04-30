/**
 * SmartMag JS functions & 3rd party libraries
 */

var Bunyad_Theme = (function($) {
	"use strict";
	
	var hasTouch = false,
	    responsive_menu = false,
	    mobile_head_init = false;
	
	// module
	return {
		
		init: function() 
		{
			
			// posts grid 
			var grid = $('.posts-grid').data('grid-count');
			if (parseInt(grid) > 0) {
				$('.posts-grid .column:nth-child(' + grid + 'n)').addClass('last');
			}
			
			// fit videos to container
			$('.featured-vid, .post-content').fitVids();

			// ratings
			$('.rate-number').each(function() {
				var raw = $(this).find('span:not(.progress)').html(),
					progress = parseFloat(raw);
				
				$(this).find('.progress').css('width', (raw.search('%') === -1 ? (Math.round(progress / 10 * 100)) + '%' : progress));
			});
			
			// Image effects - remove temp CSS when loaded
			$('.main img, .main-footer img').addClass('no-display');
			$('.bunyad-img-effects-css').remove();
			
						
			// Social icons widget
			$('.lower-foot .social-icons a, .share-links a').tooltip({placement: 'top'});
			//$('.social-icons a').tooltip({placement: 'bottom'});
			
			// Block display filters
			var term_processing;
			$('.section-head .subcats a, .block-head .filters a').click(function() {
				
				if ($(this).hasClass('active')) {
					return false;
				}
				
				var active   = $(this).parents('.subcats').find('a.active'),
					parent   = $(this).closest('section'),
					block_id = parent.data('id'), 
					term_id  = $(this).data('id'),
					content  = parent.find('.block-content');
				
				// First associated with All with id 0
				content.find('> div:first-child').attr('data-id', 0);
				
				// Add pre-loaded filter content to block 
				if (!content.find('[data-id='+ term_id +']').length) {
					if (typeof bunyad_preload == 'undefined' || !bunyad_preload[block_id]) {
						return false;
					}

					var block = $(bunyad_preload[block_id][term_id]).find('.block-content');
					block.find(' > div').hide().attr('data-id', term_id);
					block.find('img').addClass('no-display appear');

					content.append(block.html());
				}
				
				var block_ref = content.find('[data-id='+ term_id +']');
				term_processing = null;
				
				// Not ready yet, show loader
				if (!block_ref.hasClass('ready')) {
					
					content.addClass('loading');
					term_processing = term_id;
					
					var process = function() {
						
						// Some other term has been clicked
						if (term_processing !== term_id) {
							return;
						}
						
						// Show current and hide others
						content.find('> div').hide();
						
						block_ref.addClass('ready').fadeIn(500);
						content.removeClass('loading');
					};
				
					// Wait for images
					if (block_ref.find('img').length) {
						block_ref.waitForImages(true).always(process);
					}
					else {
						process();
					}
				}
				else {
					// Show current and hide others
					content.find('> div').hide();
					block_ref.fadeIn(500);
				}
				
				// Filter links active
				$(this).addClass('active');
				active.removeClass('active');
				
				return false;
			});
			
			$('.modal').on('shown.bs.modal', function() {
				$(this).css({
					'margin-top': function () {
						return -($(this).height() / 2);
					}
				});
			});
			
			// login
			$(document).on('click', '.user-login', function() {
				
				$('.login-modal .modal-content').hide();
				$('.login-modal .main-screen').show();
				
				$('#login-modal').modal('show');
				
				return false;
			});
			
			var change_modal = function(name) {
				
				if (!$('.login-modal').is(':visible')) {
					$('#login-modal').modal('show');
				}
				
				$('.login-modal .modal-content').hide();
				$('.login-modal ' + name).show();
				
				return false;
				
			};
			
			$('a.register-modal').click(function() {
				return change_modal('.register-now');
			});
			
			$('a.lost-pass-modal').click(function() {
				return change_modal('.lost-pass');
			});
			
			// setup all sliders
			this.sliders();
			
			// handle shortcodes
			this.shortcodes();
			
			// setup mobile header and navigation
			this.mobile_header();
			this.responsive_nav();
			this.touch_nav();
			
			// start the news ticker
			this.news_ticker();
			
			// setup the lightbox
			this.lightbox();
			
			// use sticky navigation if enabled
			this.sticky_nav();
			
			// use sticky sidebar if enabled
			this.sticky_sidebar();
			
			// user ratings
			this.user_ratings();
			
			// infinite scroll if enabled
			this.infinite_scroll();
			
			/**
			 * Image scroll animations
			 */
			$('.main img, .main-footer img, .main-featured .row').one('inview', function() {
				$(this).addClass('appear');
			});
			
			$('.review-box ul li .bar').each(function() {
				$(this).data('width', $(this)[0].style.width).css('width', 0);
			});
			
			$('.review-box ul li').one('inview', function() {
				var bar = $(this).find('.bar');
				bar.addClass('appear').css('width', bar.data('width'));
			});
			
			// Single top social sharing view all buttons
			$('.post-share-b .show-more').on('click', function() {
				$(this).parent().addClass('all');
				return false;
			})
			
			/**
			 * Nav Search
			 */
			$('.search-overlay .search-icon').on('click', function() {
				
				$(this).parent().toggleClass('active');
				return false;
				
			});
			
			$(document).on('click', function(e) {
				if (!$(e.target).is('.search-overlay') && !$(e.target).parents('.search-overlay').length) {
					$('.search-overlay').removeClass('active');
				}
			});
			
			// nav icons class if missing
			$('.navigation i.only-icon').each(function() {
				
				var el = $(this).closest('li');
				if (!el.hasClass('only-icon')) {
					el.addClass('only-icon');
					
					// reflow bug fix for webkit
					var nav = $('.navigation .menu ul').css('-webkit-box-sizing', 'border-box');
					requestAnimationFrame(function() {
						nav.css('-webkit-box-sizing', '');
					});
				}

			});
			
			/**
			 * IE fixes
			 */
			if ($.browser && $.browser.msie && 8 == parseInt($.browser.version)) {
				
				$('.main img, .main-footer img').addClass('no-display');
				$('.main img, .main-footer img, .main-featured .row').unbind('inview');
				
				// fontawesome4 fails to draw sometimes on IE8
			    $(function() {
			        var $ss = $('#smartmag-font-awesome-css');
			        $ss[0].href = $ss[0].href;
			    });
			    
			    // flickr widget fix - ie8 only
				$('.flickr-widget .flickr_badge_image:nth-of-type(4n)').css('margin-right', 0);

				// background image fix for IE8
				var bg = $('body').css('background-attachment'),
					bg_url = $('body').css('background-image').replace(/^url\((['"]?)(.*)\1\)$/, '$2');
			
				if (bg == 'fixed' && bg_url) {
			 							
					$('body').append('<style type="text/css">.bg-overlay { filter: progid:DXImageTransform.Microsoft.AlphaImageLoader(src=\'' + bg_url + '\', sizingMethod=\'scale\'); \
						-ms-filter: "progid:DXImageTransform.Microsoft.AlphaImageLoader(src=\'' + bg_url + '\', sizingMethod=\'scale\')"; }</style>');
					
					$('<div class="bg-overlay"></div>').appendTo('body');
				}
				
				// more lackluster ie8 
				$('.listing > .column:nth-child(odd)').css('clear', 'both');
			}
			
			// add support for placeholder in IE8/IE9
			$('input, textarea').placeholder();
			
			/**
			 * Mobile devices "background-attachment: fixed" support
			 */
			if ($(window).width() < 1128) {
				
				var bg = $('body').css('background-attachment'),
					bg_image = $('body').css('background-image');
				
				if (bg == 'fixed' && bg_image) {
					$('body').css('background-image', 'none').append(
							$('<div class="background-cover">' + '</div>').css('background-image', bg_image)
					);
				}
			}
			
			/**
			 * Woocommerce
			 */ 
			$('.woocommerce-ordering .drop li a').click(function(e) {
				var form = $(this).closest('form');
				
				form.find('[name=orderby]').val($(this).parent().data('value'));
				form.submit();
				
				e.preventDefault();
			});	
			
			$('body').on('added_to_cart', function() {
				$('.menu .widget_shopping_cart').css('opacity', '');
			});
			
			if ($('.menu .cart_list .empty').length) {
				$('.menu .cart_list').remove();
			}
			
			// Fix Firefox Bug #1149357
			if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1 && window.devicePixelRatio > 1.5) {
				
				var firefox_retina = function(sel) {
					var images = $(sel);
					if (images.length) {
						
						images.each(function() {
							
							var image = $(this);
							
							// order maters - attach event first
							$('<img />').on('load', function() {
								
								// picked 2x limage? set 1x dimension to prevent firefox overflowing
								if (image.prop('currentSrc') !== image.prop('src')) {
									image.css('width', $(this)[0].naturalWidth).css('height', $(this)[0].naturalHeight);
								}
								
							}).attr('src', image.attr('src'));
						});
					}
				};
				
				// Common areas with image width set as auto
				firefox_retina('.logo-image, .highlights .thumb img, .posts-list img');
				
				$('.section-head .subcats a, .block-head .filters a').on('click', function() {
					firefox_retina($(this).parents('.block-wrap').find('img'));
				});
			}
			
			// add android class
			if (navigator.userAgent.match(/android/i)) {
				$('body').addClass('android');
			}
			
		},
		
		news_ticker: function()
		{
			$('.trending-ticker ul').each(function() {
				
				if (!$(this).find('li.active').length) {
					$(this).find('li:first').addClass('active');
				}
				
				var ticker = $(this);
				
				window.setInterval(function() {
					
					var active = ticker.find('li.active');
					active.fadeOut(function() {
						
						var next = active.next();
						if (!next.length) {
							next = ticker.find('li:first');
						}
						
						next.addClass('active').fadeIn();
						active.removeClass('active');
					});
					
				}, 8000);
			});
		},
		
		/**
		 * Configure mobile header
		 */
		mobile_header: function() {
			
			// register resize event
			var that = this;
			
			// place in separate method to prevent mem leaks
			$(window).on('resize orientationchange', function f() {
				that.init_mobile_header();
				return f;
			}());
		},
		
		init_mobile_header: function() {
			
			if (mobile_head_init || $(window).width() > 799 || !$('body').hasClass('has-mobile-head')) {
				return;
			}
			
			// copy search form
			var search = $('.top-bar .search');
			search = (search.length ? search : $('.nav-search .search'));

			if (search.length) {
				$('.mobile-head .search-overlay').append(search.clone());
			}
			
			mobile_head_init = true;
		},
		
		/**
		 * Setup the responsive nav events and markup
		 */
		responsive_nav: function() {
			
			// detect touch capability dynamically
			$(window).on('touchstart', function() {
				hasTouch = true;
				$('body').addClass('touch');
			});
			
			this.init_responsive_nav();
			var that = this;

			$(window).on('resize orientationchange', function() {
				that.init_responsive_nav();
			});		
		},

		init_responsive_nav: function() {
			
			if ($(window).width() > 799 || responsive_menu) {
				return;
			}
			
			// set responsive initialized
			responsive_menu = true;
			
			var off_canvas = ($('.navigation .mobile').data('type') == 'off-canvas'),
			    mobile_search = false,
			    menu;
			
			/**
			 * Create the mobile menu from desktop menu
			 */
			if (!$('.navigation .mobile-menu').length) {
				
				// clone navigation for mobile
				var menu = $('.navigation div[class$="-container"]').clone().addClass('mobile-menu-container');
				
				// add category mega menu links
				menu.find('div.mega-menu .sub-cats').each(function() {
					var container = $(this).closest('.menu-item');
					
					container.append($(this).find('.sub-nav'));
					container.find('.sub-nav').replaceWith(function() {
						return $('<ul />', {html: $(this).html()});
					});
				});
				
				menu.find('.menu').addClass('mobile-menu');
				
				// append inside wrap for full width menu
				menu.appendTo(($('.navigation > .wrap').length ? '.navigation > .wrap' : '.navigation'));
			}
			else {
				menu = $('.navigation .mobile-menu-container');
			}
			
			// off-canvas setup?
			if (off_canvas) {
				menu.addClass('off-canvas');
				menu.find('.menu').prepend($('<li class="close"><a href="#"><span>' + $('.navigation .selected .text').text()  + '</span> <i class="fa fa-times"></i></a></li>'));
				$('body').addClass('nav-off-canvas');
			}
			
			// mobile search?
			if ($('.navigation .mobile').data('search')) {
				mobile_search = true;
			}
			
			// register click handlers for mobile menu
			$('.navigation .mobile .selected').click(function(e) {
				
				// search active?
				if ($(e.target).hasClass('hamburger') || !mobile_search  || !$(this).find('.search .query').is(':visible')) {
                   
                    if (off_canvas) {
                        $('.navigation .mobile-menu').addClass('active');
                    	$('body').toggleClass('off-canvas-active');
                    }
                    else {
                        $('.navigation .mobile-menu').toggleClass('active');
                    }
                    
                    return false;
				}
			});
			
			$('.mobile-head .menu-icon a').on('click', function() {
             	$('body').toggleClass('off-canvas-active');
			});
			
			
			// have custom retina mobile logo? set dimensions
			var logo_mobile = $('.mobile-head').length ? $('.mobile-head .logo-mobile') : $('.logo-mobile');
			
			if (logo_mobile.length) {
				
				// order maters - attach event first
				$('<img />').on('load', function() {
					logo_mobile.prop('width', $(this)[0].naturalWidth / 2).prop('height', $(this)[0].naturalHeight / 2);
				}).prop('src', logo_mobile.prop('src'));
			}
			
			// Fix: Retina.js 2x logo on tablets orientation change
			$(window).on('resize orientationchange', function() {
				var logo = $('.logo-image');
				if (logo.prop('width') == 0) {
					logo.prop('width', logo[0].naturalWidth / 2).prop('height', logo[0].naturalHeight / 2);
				}
			});
			
			// off-canvas close
			$('.off-canvas .close').click(function() {
				$('body').toggleClass('off-canvas-active');
			});
			
			
			// add mobile search
			if (mobile_search) {
				
				var search = $('.top-bar .search');
				search = (search.length ? search : $('.nav-search .search'));
				
				// copy from top bar or nav search
				if (search.length) {
				
					$('.navigation .mobile .selected').append(search[0].outerHTML);
					$('.mobile .search .search-button').click(function() {
		
						if (!$('.mobile .search .query').is(':visible')) {
								$('.navigation .mobile .selected .current, .navigation .mobile .selected .text').toggle();              
								$('.mobile .search').toggleClass('active');
		
								return false;
						}
					});
				}
			}
			
			// setup mobile menu click handlers
			$('.navigation .mobile-menu li > a').each(function() {
				
				if ($(this).parent().children('ul').length) {
					$('<a href="#" class="chevron"><i class="fa fa-angle-down"></i></a>').appendTo($(this));
				}
			});
			
			$('.navigation .mobile-menu li .chevron').click(function() {
					$(this).closest('li').find('ul').first().toggle().parent().toggleClass('active item-active');
					return false;
			});
			
			// add active item
			var last = $('.mobile-menu .current-menu-item').last().find('> a');
			if (last.length) {
				
				var selected = $('.navigation .mobile .selected'),
					current  = selected.find('.current'),
					cur_text = selected.find('.text').text();
				
				if (cur_text.slice(-1) !== ':') {
					selected.find('.text').text(cur_text + ':');
				}
				
				current.text(last.text());
			}
		},
		
		/**
		 * Setup touch navigation for larger touch devices
		 */
		touch_nav: function() {
			
			var targets = $('.menu:not(.mobile-menu) a'),
				open_class = 'item-active',
				child_tag = 'ul, .mega-menu';
			
			targets.each(function() {
				
				var $this = $(this),
					$parent = $this.parent('li'),
					$siblings = $parent.siblings().find('a');
				
				$this.click(function(e) {
					
					if (!hasTouch) {
						return;
					}
					
					var $this = $(this);
					e.stopPropagation();
					
					$siblings.parent('li').removeClass(open_class);
					
					// has a child? open the menu on tap
					if (!$this.parent().hasClass(open_class) && $this.next(child_tag).length > 0 && !$this.parents('.mega-menu.links').length) {
						e.preventDefault();
						$this.parent().addClass(open_class);
					}
				});
			});
			
			// close all menus
			$(document).click(function(e) {
				if (!$(e.target).is('.menu') && !$(e.target).parents('.menu').length) {
					targets.parent('li').removeClass(open_class);
				}
			});
		},
		
		/**
		 * Setup sticky navigation if enabled
		 */
		sticky_nav: function()
		{
			var nav = $('.navigation-wrap'),
			    nav_top  = nav.offset().top,
			    smart = (nav.data('sticky-type') == 'smart'),
			    is_sticky = false,
			    prev_scroll = 0,
			    cur_scroll;
			
			// Not enabled?
			if (!nav.data('sticky-nav')) {
				return;
			}
			
			if (nav.find('.sticky-logo').length) {
				nav.addClass('has-logo');
			}
			
			// Set height for container when icons etc. have loaded
			var set_size = function() {
				$('.main-nav').css('min-height', nav.height());
			};
			
			$(window).on('load resize', set_size);
			
			// Disable the sticky nav
			var remove_sticky = function() {
				
				// check before dom modification 
				if (is_sticky) {
					nav.removeClass('sticky-nav');
					set_size();
				}
			};
			
			// Make the nav sticky
			var sticky = function() {

				if (!nav.data('sticky-nav') || $(window).width() < 800) {
					return;
				}
				
				cur_scroll = $(window).scrollTop();
				is_sticky  = nav.hasClass('sticky-nav');
				
				// make it sticky when viewport is scrolled beyond the navigation
				if ($(window).scrollTop() > nav_top) {
					
					// for smart sticky, test for scroll change
					if (smart && (!prev_scroll || cur_scroll > prev_scroll)) {
						remove_sticky();
					}
					else {
						
						if (!nav.hasClass('sticky-nav')) {
							nav.addClass('sticky-nav no-transition');
						
							setTimeout(function() { 
								nav.removeClass('no-transition'); 
							}, 100);
						}
					}
					
					prev_scroll = cur_scroll;
					
				} else {
					remove_sticky();
				}
			};

			sticky();

			$(window).scroll(function() {
				sticky();
			});
			
		},
		
		/**
		 * Setup sticky sidebar
		 */
		sticky_sidebar: function() 
		{
			var sticky = $('.sidebar').data('sticky');
			if (!sticky) {
				return;
			}
			
			$('.main .sidebar').theiaStickySidebar({minWidth: 800, updateSidebarHeight: false});
		},
		
		/**
		 * Setup all the sliders available
		 */
		sliders: function()
		{
			if (!$.fn.flexslider) {
				return;
			}
			
			var is_rtl = ($('html').attr('dir') == 'rtl' ? true : false);
			
			// main slider
			var slider = $('.main-featured .slider');
			
			$('.main-featured .flexslider').flexslider({
				controlNav: true,
				animationSpeed: slider.data('animation-speed'),
				animation: slider.data('animation'),
				slideshowSpeed: slider.data('slide-delay'),
				manualControls: '.main-featured .flexslider .pages a',
				pauseOnHover: true,
				start: function() {
					$('.main-featured .slider').css('opacity', 1);
				},
				rtl: is_rtl
			});
			
			// main slider dynamic pagination - if not at default of 5
			var pages  = $('.main-featured .pages'),
				number = parseInt(pages.data('number'));
			
			if (number && number != 5) {
				var width = (100 - ((number + 1) * 0.284900285)) / number;  // 100 - (slides + 1 * margin-left) / slides
				pages.find('a').css('width', width + '%');
			}
			
			// carousels / galleries
			$('.carousel').flexslider({
				animation: 'slide',
				animationLoop: false,
				itemWidth: 214,
				itemMargin: 30,
				minItems: 3,
				maxItems: 4,
				controlNav: false,
				slideshow: false,
				rtl: is_rtl
				
			});
			
			$('.gallery-block .flexslider').flexslider({
				controlNav: false,
				pauseOnHover: true,
				rtl: is_rtl
			});
			
			// for post-galleries
			$('.gallery-slider .flexslider').flexslider({
				controlNav: false,
				pauseOnHover: true,
				rtl: is_rtl
			});
			
			// post galleries in post cover
			$('.post-cover .gallery-slider li, .post-cover .featured').each(function() {
				var img = $(this).find('img');
				$(this).css('background-image', 'url("' + img.attr('src') + '")');
				img.addClass('hidden');
			});
			
			/**
			 * Post Content Slideshow: AJAX
			 */
			var slideshow_cache = {},
				slideshow_wrap  = '.post-slideshow .post-pagination-next';
			
			if ($(slideshow_wrap).length && $(slideshow_wrap).data('type') == 'ajax') {
			
				var processing;
				
				$('.main-content').on('click', '.post-slideshow .post-pagination-next .links a', function() {
					
						// showing on home-page?
						if ($('body').hasClass('page')) {
							return;
						}
						
						// bottom links, scroll top
						var scroll;
						if ($(this).parents('.bottom').length) {
							scroll = true;
						}
						
						// abort existing request
						if (processing && processing.hasOwnProperty('abort')) {
							processing.abort();
						}
					
						var parent = $(this).closest('.post-slideshow'),
							url    = $(this).attr('href');
						
						parent.find('.content-page').removeClass('active').addClass('hidden previous');
					
						var show_slide = function(data) {
							
							// change browser url
							if (history.pushState) {
								history.pushState({}, '', url);
							}
							
							var page = $(data).find('.post-slideshow');
							
							if (page.length) {
								parent.find('.post-pagination-next').html(page.find('.post-pagination-next').html());
								parent.find('.content-page').after(page.find('.content-page').addClass('hidden loading'));
								
								setTimeout(function() {

									if (scroll) {
										$('html, body').animate({scrollTop: parent.offset().top - 50}, 200);
									}
									
									parent.find('.content-page.previous').remove();
									parent.find('.content-page.loading')
										.removeClass('previous hidden loading')
										.find('img').addClass('appear');
								}, 1);
							}
							
							processing = null;
							
						};
						
						// in cache?
						if (slideshow_cache[url]) {
							show_slide(slideshow_cache[url]);
						}
						else {
							
							// get via ajax
							processing = $.get(url, function(data) {
								slideshow_cache[url] = data;
								show_slide(data);
								
							});
						}
						
						return false;
				});
				
				// keyboard nav
				$(document).on('keyup', function(e) {				
						if (e.which == 37) {
							$(slideshow_wrap).find('.prev').parent().click();
						}
						else if (e.which == 39) {
							$(slideshow_wrap).find('.next').parent().click();
						}
				});
				
			} // end slideshow wrap
			
			
			// Object-fit polyfill
			var images = $('.featured-grid-b .image-link img');
			if (images.length) {
				objectFitImages(null, {watchMQ: true});
			}
		},
		
		/**
		 * Register shortcode related events
		 */
		shortcodes: function()
		{
			// normal tabs
			$('.tabs-list a').click(function() {
				
				var tab = $(this).data('tab'),
					tabs_data = $(this).closest('.tabs-list').siblings('.tabs-data'),
					parent = $(this).parent().parent(),
					active = parent.find('.active');
				
				if (!active.length) {
					active = parent.find('li:first-child');
				}

				active.removeClass('active').addClass('inactive');
				$(this).parent().addClass('active').removeClass('inactive');
				
				// hide current and show the clicked one
				var active_data = tabs_data.find('.tab-posts.active');
				if (!active_data.length) {
					active_data = tabs_data.find('.tab-posts:first-child');
				}
				
				active_data.hide();
				
				tabs_data.find('#recent-tab-' + tab).fadeIn().addClass('active').removeClass('inactive');

				return false;
				
			});
			
			/**
			 * Shortcode: Tabs
			 */
			$('.sc-tabs a').click(function() {
	
				// tabs first
				var tabs = $(this).parents('ul');
				tabs.find('.active').removeClass('active');
				$(this).parent().addClass('active');
				
				// panes second
				var panes = tabs.siblings('.sc-tabs-panes');
				
				panes.find('.active').hide().removeClass('active');
				panes.find('#sc-pane-' + $(this).data('id')).addClass('active').fadeIn();
				
				return false;
			});
			
			/**
			 * Shortcode: Accordions & Toggles
			 */
			$('.sc-accordion-title > a').click(function() {
				
				var container = $(this).parents('.sc-accordions');
				container.find('.sc-accordion-title').removeClass('active');
				container.find('.sc-accordion-pane').slideUp().removeClass('active');
				
				var pane = $(this).parent().next();
				if (!pane.is(':visible')) {
					$(this).parent().addClass('active');
					pane.slideDown().addClass('active');
				}
				
				return false;
			});
			
			$('.sc-toggle-title > a').click(function() {
				$(this).parent().toggleClass('active');
				$(this).parent().next().slideToggle().toggleClass('active');
				
				return false;
			});
	
		},
		
		/**
		 * User Ratings handling
		 */
		user_ratings: function() 
		{
			
			var compute_percent = function(e) {
				
				
				var offset = $(this).offset(),
				    position, percent;
				
				// count from right for RTL
				if ($('html').attr('dir') == 'rtl')  {
					offset.left = offset.left + $(this).outerWidth();
				}
				
				position = Math.abs(e.pageX - Math.max(0, offset.left));
				percent  = Math.min(100, Math.round(position / $(this).width() * 100));
				
				return percent;
			};

			// percent or points?
			var is_points = true,
				scale = parseInt($('.review-box .value-title').text()) || 10;
			
			if ($('.review-box .overall .percent').length) {
				is_points = false;
			}
			
			// update the bar and percent/points on hover
			$('.user-ratings .main-stars, .user-ratings .rating-bar').on('mousemove mouseenter mouseleave', 
				function(e) {
				
					// set main variables
					var bar = $(this).find('span'),
						user_ratings = $(this).closest('.user-ratings');
				
					bar.css('transition', 'none');
					
					if (user_ratings.hasClass('voted')) {
						return;
					}
				
					// hover over?
					if (e.type == 'mouseleave') {
						bar.css('width', bar.data('orig-width'));
						user_ratings.find('.hover-number').hide();
						user_ratings.find('.rating').show();
						return;
					}
					
					var percent = compute_percent.call(this, e);
					
					if (!bar.data('orig-width')) {
						bar.data('orig-width', bar[0].style.width);
					}
					
					bar.css('width', percent + '%');
					user_ratings.find('.rating').hide();
					user_ratings.find('.hover-number').show().text((is_points ? +parseFloat(percent / 100 * scale).toFixed(1) : percent + '%'));
				}
			);
			
			// add the rating
			$('.user-ratings .main-stars, .user-ratings .rating-bar').on('click', function(e) {
				
				// set main variables
				var bar = $(this).find('span'),
					user_ratings = $(this).closest('.user-ratings');
				
				if (user_ratings.hasClass('voted')) {
					return;
				}
				
				// setup ajax post data
				var post_data = {
						'action': 'bunyad_rate', 
						'id': user_ratings.data('post-id'), 
						'rating': compute_percent.call(this, e)
				};
				
				// get current votes
				var votes = user_ratings.find('.number'),
					cur_votes = parseInt(votes.text()) || 0;
				
				user_ratings.css('opacity', '0.3');
				bar.data('orig-width', bar[0].style.width);
				
				// add to votes and disable further voting 
				votes.text((cur_votes + 1).toString());
				
				$(this).trigger('mouseleave');
				user_ratings.addClass('voted');
				
				$.post(Bunyad.ajaxurl, post_data, function(data) {
					
					// update data
					if (data === Object(data)) {

						// change rating
						var cur_rating = user_ratings.find('.rating').text();
						user_ratings.find('.rating').text( cur_rating.search('%') !== -1 ? data.percent + ' %' : data.decimal );
						
						bar.css('width', data.percent + '%');
						bar.data('orig-width', data.percent);
					}
					
					user_ratings.hide().css('opacity', 1).fadeIn('slow');			
				}, 'json');
			});
		},
		
		/**
		 * Infinite Scroll
		 */
		infinite_scroll: function() 
		{
			// require jquery plugin
			if (!$.fn.infinitescroll) {
				return;
			}
				
			$('.listing-classic, .listing, .listing-alt, .list-timeline').filter(function() { if ($(this).data('infinite')) { return true; } }).each(function() {
				var that = this,
					data_sel = '[data-infinite="' + $(this).data('infinite') + '"]',
					timeline = false,
					instance, 
					opts;
				
				// infinitescroll options
				var options = {
					loading: {
						finishedMsg: '',
						msg: $('<div class="ajax-loading"><div class="spinner"><span></span><span></span><span></span></div>')
					},
					navSelector: '.main-pagination',
					nextSelector: '.main-pagination .next',
					itemSelector: data_sel + ' > .column,' + data_sel + ' > .post,' +  data_sel + ' > .post,' + data_sel + ' > .month'
				};
				
				// is timeline listing?
				if ($(this).hasClass('list-timeline')) {
					timeline = true;
					options.appendCallback = false;
				}
				
				/**
				 * Main callback when data is loaded via $.infinitescroll
				 */
				var callback = function(data) {
					
					// handle timeline listing
					if (timeline == true) {
						
						$(data).each(function() {
							var month = $(this).data('month'),
								existing = $(data_sel + ' .month[data-month="' + month + '"] .posts');
							
							// month container exists
							if (existing.length) {
								existing.append($(this).find('.posts article'));
							}
							else {
								$(data_sel).append($(this));
							}
						});
					}

					// re-bind the inview image animations
					$(that).find('img').addClass('no-display').one('inview', function() {
						$(this).addClass('appear');
					});
					
					$(window).trigger('checkInView.inview');
					$(window).trigger('resize'); // for sticky sidebar
				};
				
				// setup infinitescroll instance and set callbacks
				instance = new $.infinitescroll(options, callback, this);
				opts     = instance.options;
				
				// overwrite start event
				opts.loading.start = function() {
					
					$(opts.loading.msg).insertAfter(that).show();
					instance.beginAjax(opts);
					
					// for sticky sidebar
					$(window).trigger('resize');
				};
				
				opts.errorCallback = function() {
					$(opts.loading.msg).hide();
					
					// for sticky sidebar
					$(window).trigger('resize');
				};
				
				// hide pagination if valid infinite scroll page
				if (!opts.state.isInvalidPage) {
					$(this).parent().find('.main-pagination').hide();	
				}
			});
		
		},
		
		
		/**
		 * Setup prettyPhoto
		 */
		lightbox: function() {
			
			// disabled on mobile screens
			if (!$.fn.prettyPhoto || $(window).width() < 700) {
				return;
			}
			
			var filter_images = function() {
				
				if (!$(this).attr('href')) {
					return false;
				}
				
				return $(this).attr('href').match(/\.(jpe?g|png|bmp|gif)$/); 
			};
			
			(function() {
				var gal_id = 1;
				
				$('.post-content a, .main .featured a').has('img').filter(filter_images).attr('rel', 'prettyPhoto');
				
				$('.gallery-slider, .post-content .gallery, .post-content .tiled-gallery').each(function() {
					gal_id++; // increment gallery group id
					
					$(this).find('a').has('img').filter(filter_images)
						.attr('rel', 'prettyPhoto[gal_'+ gal_id +']');
				});
				
				$("a[rel^='prettyPhoto']").prettyPhoto({social_tools: false});
				
			})();
			
			// WooCommerce lightbox
			$('a[data-rel^="prettyPhoto"], a.zoom').prettyPhoto({hook: 'data-rel', social_tools: false});
			
		}
	}; // end return
	
})(jQuery);

// load when ready
jQuery(function($) {
		
	Bunyad_Theme.init();
});

/**
 * Live Search Handler
 */
var Bunyad_Live_Search = (function($) {
	"use strict";
	
	var cache = {}, timer, element;
	
	return {
		
		init: function() {
			
			var self = this,
			    search = $('.live-search-query');

			if (!search.length) {
				return;
			}
			
			// turn off browser's own auto-complete
			$('.live-search-query').attr('autocomplete', 'off');
			
			// setup the live search on key press
			$('.live-search-query').on('keyup', function() {
				
				element = $(this).parent();
				
				var query = $(this).val(), result;
				
				
				// clear existing debounce
				clearTimeout(timer);
				
				// minimum of 1 character
				if (query.length < 1) {
					self.add_result('');
					return;
				}
				
				// debounce to prevent excessive ajax queries
				timer = setTimeout(function() {
					self.process(query);
				}, 250);
			});
			
			// setup hide 
			$(document).on('click', function(e) {
				
				var results = $('.live-search-results');
				
				if (results.is(':visible') && !$(e.target).closest('.search').length) {
					results.removeClass('fade-in');
				}
			});
		},
		
		/**
		 * Process the search query
		 */
		process: function(query) {
			
			var self = this;
			
			// have it in cache?
			if (query in cache) {
				self.add_result(cache[query]);
			}
			else {
				$.get(Bunyad.ajaxurl, {action: 'bunyad_live_search', 'query': query}, function(data) {
					
					// add to cache and add results
					cache[query] = data;
					self.add_result(data);
				});
			}
		},
		
		/**
		 * Add live results to the container
		 */
		add_result: function(result) {
			
			if (!element.find('.live-search-results').length) {
				element.append($('<div class="live-search-results"></div>'));
			}
			
			var container = element.find('.live-search-results');

			if (!result) {
				container.removeClass('fade-in');
				return;
			}
			
			// add the html result
			container.html(result);
			
			requestAnimationFrame(function() {
				container.addClass('fade-in');
			});
			
		}
	};
	
})(jQuery);

// fire up when ready
jQuery(function() {
	Bunyad_Live_Search.init();
});

/**
 * Plugins and 3rd Party Libraries
 */

/**
 * Author Christopher Blum
 * Based on the idea of Remy Sharp, http://remysharp.com/2009/01/26/element-in-view-event-plugin/
 * 
 * License: WTFPL
 */
!function(a){"function"==typeof define&&define.amd?define(["jquery"],a):"object"==typeof exports?module.exports=a(require("jquery")):a(jQuery)}(function(a){function i(){var b,c,d={height:f.innerHeight,width:f.innerWidth};return d.height||(b=e.compatMode,(b||!a.support.boxModel)&&(c="CSS1Compat"===b?g:e.body,d={height:c.clientHeight,width:c.clientWidth})),d}function j(){return{top:f.pageYOffset||g.scrollTop||e.body.scrollTop,left:f.pageXOffset||g.scrollLeft||e.body.scrollLeft}}function k(){if(b.length){var e=0,f=a.map(b,function(a){var b=a.data.selector,c=a.$element;return b?c.find(b):c});for(c=c||i(),d=d||j();e<b.length;e++)if(a.contains(g,f[e][0])){var h=a(f[e]),k={height:h[0].offsetHeight,width:h[0].offsetWidth},l=h.offset(),m=h.data("inview");if(!d||!c)return;l.top+k.height>d.top&&l.top<d.top+c.height&&l.left+k.width>d.left&&l.left<d.left+c.width?m||h.data("inview",!0).trigger("inview",[!0]):m&&h.data("inview",!1).trigger("inview",[!1])}}}var c,d,h,b=[],e=document,f=window,g=e.documentElement;a.event.special.inview={add:function(c){b.push({data:c,$element:a(this),element:this}),!h&&b.length&&(h=setInterval(k,250))},remove:function(a){for(var c=0;c<b.length;c++){var d=b[c];if(d.element===this&&d.data.guid===a.guid){b.splice(c,1);break}}b.length||(clearInterval(h),h=null)}},a(f).on("scroll resize scrollstop",function(){c=d=null}),!g.addEventListener&&g.attachEvent&&g.attachEvent("onfocusin",function(){d=null})});

/**
* Bootstrap.js by @fat & @mdo
* plugins: bootstrap-tooltip.js
* Copyright 2012 Twitter, Inc.
* http://www.apache.org/licenses/LICENSE-2.0.txt
*/
!function(a){var b=function(a,b){this.init("tooltip",a,b)};b.prototype={constructor:b,init:function(b,c,d){var e,f;this.type=b,this.$element=a(c),this.options=this.getOptions(d),this.enabled=!0,this.options.trigger=="click"?this.$element.on("click."+this.type,this.options.selector,a.proxy(this.toggle,this)):this.options.trigger!="manual"&&(e=this.options.trigger=="hover"?"mouseenter":"focus",f=this.options.trigger=="hover"?"mouseleave":"blur",this.$element.on(e+"."+this.type,this.options.selector,a.proxy(this.enter,this)),this.$element.on(f+"."+this.type,this.options.selector,a.proxy(this.leave,this))),this.options.selector?this._options=a.extend({},this.options,{trigger:"manual",selector:""}):this.fixTitle()},getOptions:function(b){return b=a.extend({},a.fn[this.type].defaults,b,this.$element.data()),b.delay&&typeof b.delay=="number"&&(b.delay={show:b.delay,hide:b.delay}),b},enter:function(b){var c=a(b.currentTarget)[this.type](this._options).data(this.type);if(!c.options.delay||!c.options.delay.show)return c.show();clearTimeout(this.timeout),c.hoverState="in",this.timeout=setTimeout(function(){c.hoverState=="in"&&c.show()},c.options.delay.show)},leave:function(b){var c=a(b.currentTarget)[this.type](this._options).data(this.type);this.timeout&&clearTimeout(this.timeout);if(!c.options.delay||!c.options.delay.hide)return c.hide();c.hoverState="out",this.timeout=setTimeout(function(){c.hoverState=="out"&&c.hide()},c.options.delay.hide)},show:function(){var a,b,c,d,e,f,g;if(this.hasContent()&&this.enabled){a=this.tip(),this.setContent(),this.options.animation&&a.addClass("fade"),f=typeof this.options.placement=="function"?this.options.placement.call(this,a[0],this.$element[0]):this.options.placement,b=/in/.test(f),a.detach().css({top:0,left:0,display:"block"}).insertAfter(this.$element),c=this.getPosition(b),d=a[0].offsetWidth,e=a[0].offsetHeight;switch(b?f.split(" ")[1]:f){case"bottom":g={top:c.top+c.height,left:c.left+c.width/2-d/2};break;case"top":g={top:c.top-e,left:c.left+c.width/2-d/2};break;case"left":g={top:c.top+c.height/2-e/2,left:c.left-d};break;case"right":g={top:c.top+c.height/2-e/2,left:c.left+c.width}}a.offset(g).addClass(f).addClass("in")}},setContent:function(){var a=this.tip(),b=this.getTitle();a.find(".tooltip-inner")[this.options.html?"html":"text"](b),a.removeClass("fade in top bottom left right")},hide:function(){function d(){var b=setTimeout(function(){c.off(a.support.transition.end).detach()},500);c.one(a.support.transition.end,function(){clearTimeout(b),c.detach()})}var b=this,c=this.tip();return c.removeClass("in"),a.support.transition&&this.$tip.hasClass("fade")?d():c.detach(),this},fixTitle:function(){var a=this.$element;(a.attr("title")||typeof a.attr("data-original-title")!="string")&&a.attr("data-original-title",a.attr("title")||"").removeAttr("title")},hasContent:function(){return this.getTitle()},getPosition:function(b){return a.extend({},b?{top:0,left:0}:this.$element.offset(),{width:this.$element[0].offsetWidth,height:this.$element[0].offsetHeight})},getTitle:function(){var a,b=this.$element,c=this.options;return a=b.attr("data-original-title")||(typeof c.title=="function"?c.title.call(b[0]):c.title),a},tip:function(){return this.$tip=this.$tip||a(this.options.template)},validate:function(){this.$element[0].parentNode||(this.hide(),this.$element=null,this.options=null)},enable:function(){this.enabled=!0},disable:function(){this.enabled=!1},toggleEnabled:function(){this.enabled=!this.enabled},toggle:function(b){var c=a(b.currentTarget)[this.type](this._options).data(this.type);c[c.tip().hasClass("in")?"hide":"show"]()},destroy:function(){this.hide().$element.off("."+this.type).removeData(this.type)}};var c=a.fn.tooltip;a.fn.tooltip=function(c){return this.each(function(){var d=a(this),e=d.data("tooltip"),f=typeof c=="object"&&c;e||d.data("tooltip",e=new b(this,f)),typeof c=="string"&&e[c]()})},a.fn.tooltip.Constructor=b,a.fn.tooltip.defaults={animation:!0,placement:"top",selector:!1,template:'<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',trigger:"hover",title:"",delay:0,html:!1},a.fn.tooltip.noConflict=function(){return a.fn.tooltip=c,this}}(window.jQuery);

/**
* Bootstrap.js by @fat & @mdo
* plugins: bootstrap-modal.js
* Copyright 2013 Twitter, Inc.
* http://www.apache.org/licenses/LICENSE-2.0.txt
*/
!function(a){var b=function(b,c){this.options=c,this.$element=a(b).delegate('[data-dismiss="modal"]',"click.dismiss.modal",a.proxy(this.hide,this)),this.options.remote&&this.$element.find(".modal-body").load(this.options.remote)};b.prototype={constructor:b,toggle:function(){return this[this.isShown?"hide":"show"]()},show:function(){var b=this,c=a.Event("show");this.$element.trigger(c);if(this.isShown||c.isDefaultPrevented())return;this.isShown=!0,this.escape(),this.backdrop(function(){var c=a.support.transition&&b.$element.hasClass("fade");b.$element.parent().length||b.$element.appendTo(document.body),b.$element.show(),c&&b.$element[0].offsetWidth,b.$element.addClass("in").attr("aria-hidden",!1),b.enforceFocus(),c?b.$element.one(a.support.transition.end,function(){b.$element.focus().trigger("shown")}):b.$element.focus().trigger("shown")})},hide:function(b){b&&b.preventDefault();var c=this;b=a.Event("hide"),this.$element.trigger(b);if(!this.isShown||b.isDefaultPrevented())return;this.isShown=!1,this.escape(),a(document).off("focusin.modal"),this.$element.removeClass("in").attr("aria-hidden",!0),a.support.transition&&this.$element.hasClass("fade")?this.hideWithTransition():this.hideModal()},enforceFocus:function(){var b=this;a(document).on("focusin.modal",function(a){b.$element[0]!==a.target&&!b.$element.has(a.target).length&&b.$element.focus()})},escape:function(){var a=this;this.isShown&&this.options.keyboard?this.$element.on("keyup.dismiss.modal",function(b){b.which==27&&a.hide()}):this.isShown||this.$element.off("keyup.dismiss.modal")},hideWithTransition:function(){var b=this,c=setTimeout(function(){b.$element.off(a.support.transition.end),b.hideModal()},500);this.$element.one(a.support.transition.end,function(){clearTimeout(c),b.hideModal()})},hideModal:function(){var a=this;this.$element.hide(),this.backdrop(function(){a.removeBackdrop(),a.$element.trigger("hidden")})},removeBackdrop:function(){this.$backdrop&&this.$backdrop.remove(),this.$backdrop=null},backdrop:function(b){var c=this,d=this.$element.hasClass("fade")?"fade":"";if(this.isShown&&this.options.backdrop){var e=a.support.transition&&d;this.$backdrop=a('<div class="modal-backdrop '+d+'" />').appendTo(document.body),this.$backdrop.click(this.options.backdrop=="static"?a.proxy(this.$element[0].focus,this.$element[0]):a.proxy(this.hide,this)),e&&this.$backdrop[0].offsetWidth,this.$backdrop.addClass("in");if(!b)return;e?this.$backdrop.one(a.support.transition.end,b):b()}else!this.isShown&&this.$backdrop?(this.$backdrop.removeClass("in"),a.support.transition&&this.$element.hasClass("fade")?this.$backdrop.one(a.support.transition.end,b):b()):b&&b()}};var c=a.fn.modal;a.fn.modal=function(c){return this.each(function(){var d=a(this),e=d.data("modal"),f=a.extend({},a.fn.modal.defaults,d.data(),typeof c=="object"&&c);e||d.data("modal",e=new b(this,f)),typeof c=="string"?e[c]():f.show&&e.show()})},a.fn.modal.defaults={backdrop:!0,keyboard:!0,show:!0},a.fn.modal.Constructor=b,a.fn.modal.noConflict=function(){return a.fn.modal=c,this},a(document).on("click.modal.data-api",'[data-toggle="modal"]',function(b){var c=a(this),d=c.attr("href"),e=a(c.attr("data-target")||d&&d.replace(/.*(?=#[^\s]+$)/,"")),f=e.data("modal")?"toggle":a.extend({remote:!/#/.test(d)&&d},e.data(),c.data());b.preventDefault(),e.modal(f).one("hide",function(){c.focus()})})}(window.jQuery);

/*!
* FitVids 1.1
*
* Copyright 2013, Chris Coyier - http://css-tricks.com + Dave Rupert - http://daverupert.com
* Credit to Thierry Koblentz - http://www.alistapart.com/articles/creating-intrinsic-ratios-for-video/
* Released under the WTFPL license - http://sam.zoy.org/wtfpl/
*
*/
;(function($){$.fn.fitVids=function(options){var settings={customSelector:null,ignore:null};if(!document.getElementById("fit-vids-style")){var head=document.head||document.getElementsByTagName("head")[0];var css=".fluid-width-video-wrapper{width:100%;position:relative;padding:0;}.fluid-width-video-wrapper iframe,.fluid-width-video-wrapper object,.fluid-width-video-wrapper embed {position:absolute;top:0;left:0;width:100%;height:100%;}";var div=document.createElement("div");div.innerHTML='<p>x</p><style id="fit-vids-style">'+css+"</style>";head.appendChild(div.childNodes[1])}if(options){$.extend(settings,options)}return this.each(function(){var selectors=['iframe[src*="player.vimeo.com"]','iframe[src*="youtube.com"]','iframe[src*="youtube-nocookie.com"]','iframe[src*="kickstarter.com"][src*="video.html"]',"object","embed"];if(settings.customSelector){selectors.push(settings.customSelector)}var ignoreList=".fitvidsignore";if(settings.ignore){ignoreList=ignoreList+", "+settings.ignore}var $allVideos=$(this).find(selectors.join(","));$allVideos=$allVideos.not("object object");$allVideos=$allVideos.not(ignoreList);$allVideos.each(function(){var $this=$(this);if($this.parents(ignoreList).length>0){return}if(this.tagName.toLowerCase()==="embed"&&$this.parent("object").length||$this.parent(".fluid-width-video-wrapper").length){return}if((!$this.css("height")&&!$this.css("width"))&&(isNaN($this.attr("height"))||isNaN($this.attr("width")))){$this.attr("height",9);$this.attr("width",16)}var height=(this.tagName.toLowerCase()==="object"||($this.attr("height")&&!isNaN(parseInt($this.attr("height"),10))))?parseInt($this.attr("height"),10):$this.height(),width=!isNaN(parseInt($this.attr("width"),10))?parseInt($this.attr("width"),10):$this.width(),aspectRatio=height/width;if(!$this.attr("id")){var videoID="fitvid"+Math.floor(Math.random()*999999);$this.attr("id",videoID)}$this.wrap('<div class="fluid-width-video-wrapper"></div>').parent(".fluid-width-video-wrapper").css("padding-top",(aspectRatio*100)+"%");$this.removeAttr("height").removeAttr("width")})})}})(window.jQuery||window.Zepto);

/**
 * Plus/minus polyfill for numbers - used in WooCommerce
 * 
 * Author Bryce Adams
 */
!function($){$("div.quantity:not(.buttons_added), td.quantity:not(.buttons_added)").addClass("buttons_added").append('<input type="button" value="+" class="plus" />').prepend('<input type="button" value="-" class="minus" />'),$(document).on("click",".plus, .minus",function(){var t=$(this).closest(".quantity").find(".qty"),a=parseFloat(t.val()),n=parseFloat(t.attr("max")),s=parseFloat(t.attr("min")),e=t.attr("step");a&&""!==a&&"NaN"!==a||(a=0),(""===n||"NaN"===n)&&(n=""),(""===s||"NaN"===s)&&(s=0),("any"===e||""===e||void 0===e||"NaN"===parseFloat(e))&&(e=1),$(this).is(".plus")?t.val(n&&(n==a||a>n)?n:a+parseFloat(e)):s&&(s==a||s>a)?t.val(s):a>0&&t.val(a-parseFloat(e)),t.trigger("change")})}(jQuery);


/*! http://mths.be/placeholder v2.0.7 by @mathias */
(function(q,f,d){function r(b){var a={},c=/^jQuery\d+$/;d.each(b.attributes,function(b,d){d.specified&&!c.test(d.name)&&(a[d.name]=d.value)});return a}function g(b,a){var c=d(this);if(this.value==c.attr("placeholder")&&c.hasClass("placeholder"))if(c.data("placeholder-password")){c=c.hide().next().show().attr("id",c.removeAttr("id").data("placeholder-id"));if(!0===b)return c[0].value=a;c.focus()}else this.value="",c.removeClass("placeholder"),this==m()&&this.select()}function k(){var b,a=d(this),c=this.id;if(""==this.value){if("password"==this.type){if(!a.data("placeholder-textinput")){try{b=a.clone().attr({type:"text"})}catch(e){b=d("<input>").attr(d.extend(r(this),{type:"text"}))}b.removeAttr("name").data({"placeholder-password":a,"placeholder-id":c}).bind("focus.placeholder",g);a.data({"placeholder-textinput":b,"placeholder-id":c}).before(b)}a=a.removeAttr("id").hide().prev().attr("id",c).show()}a.addClass("placeholder");a[0].value=a.attr("placeholder")}else a.removeClass("placeholder")}function m(){try{return f.activeElement}catch(b){}}var h="placeholder"in f.createElement("input"),l="placeholder"in f.createElement("textarea"),e=d.fn,n=d.valHooks,p=d.propHooks;h&&l?(e=e.placeholder=function(){return this},e.input=e.textarea=!0):(e=e.placeholder=function(){this.filter((h?"textarea":":input")+"[placeholder]").not(".placeholder").bind({"focus.placeholder":g,"blur.placeholder":k}).data("placeholder-enabled",!0).trigger("blur.placeholder");return this},e.input=h,e.textarea=l,e={get:function(b){var a=d(b),c=a.data("placeholder-password");return c?c[0].value:a.data("placeholder-enabled")&&a.hasClass("placeholder")?"":b.value},set:function(b,a){var c=d(b),e=c.data("placeholder-password");if(e)return e[0].value=a;if(!c.data("placeholder-enabled"))return b.value=a;""==a?(b.value=a,b!=m()&&k.call(b)):c.hasClass("placeholder")?g.call(b,!0,a)||(b.value=a):b.value=a;return c}},h||(n.input=e,p.value=e),l||(n.textarea=e,p.value=e),d(function(){d(f).delegate("form","submit.placeholder",function(){var b=d(".placeholder",this).each(g);setTimeout(function(){b.each(k)},10)})}),d(q).bind("beforeunload.placeholder",function(){d(".placeholder").each(function(){this.value=""})}))})(this,document,jQuery);

// requestAnimationFrame pollyfill by paulirish - MIT
(function(){for(var e=0,b=["ms","moz","webkit","o"],a=0;a<b.length&&!window.requestAnimationFrame;++a)window.requestAnimationFrame=window[b[a]+"RequestAnimationFrame"],window.cancelAnimationFrame=window[b[a]+"CancelAnimationFrame"]||window[b[a]+"CancelRequestAnimationFrame"];window.requestAnimationFrame||(window.requestAnimationFrame=function(a,b){var c=(new Date).getTime(),d=Math.max(0,16-(c-e)),f=window.setTimeout(function(){a(c+d)},d);e=c+d;return f});window.cancelAnimationFrame||(window.cancelAnimationFrame=function(a){clearTimeout(a)})})();

/*! npm.im/object-fit-images */
var objectFitImages=function(){"use strict";function t(t){for(var e,r=getComputedStyle(t).fontFamily,i={};null!==(e=c.exec(r));)i[e[1]]=e[2];return i}function e(e,i){if(!e[n].parsingSrcset){var s=t(e);if(s["object-fit"]=s["object-fit"]||"fill",!e[n].s){if("fill"===s["object-fit"])return;if(!e[n].skipTest&&l&&!s["object-position"])return}var c=e[n].ios7src||e.currentSrc||e.src;if(i)c=i;else if(e.srcset&&!u&&window.picturefill){var o=window.picturefill._;e[n].parsingSrcset=!0,e[o.ns]&&e[o.ns].evaled||o.fillImg(e,{reselect:!0}),e[o.ns].curSrc||(e[o.ns].supported=!1,o.fillImg(e,{reselect:!0})),delete e[n].parsingSrcset,c=e[o.ns].curSrc||c}if(e[n].s)e[n].s=c,i&&(e[n].srcAttr=i);else{e[n]={s:c,srcAttr:i||f.call(e,"src"),srcsetAttr:e.srcset},e.src=n;try{e.srcset&&(e.srcset="",Object.defineProperty(e,"srcset",{value:e[n].srcsetAttr})),r(e)}catch(t){e[n].ios7src=c}}e.style.backgroundImage='url("'+c+'")',e.style.backgroundPosition=s["object-position"]||"center",e.style.backgroundRepeat="no-repeat",/scale-down/.test(s["object-fit"])?(e[n].i||(e[n].i=new Image,e[n].i.src=c),function t(){return e[n].i.naturalWidth?void(e[n].i.naturalWidth>e.width||e[n].i.naturalHeight>e.height?e.style.backgroundSize="contain":e.style.backgroundSize="auto"):void setTimeout(t,100)}()):e.style.backgroundSize=s["object-fit"].replace("none","auto").replace("fill","100% 100%")}}function r(t){var r={get:function(){return t[n].s},set:function(r){return delete t[n].i,e(t,r),r}};Object.defineProperty(t,"src",r),Object.defineProperty(t,"currentSrc",{get:r.get})}function i(){a||(HTMLImageElement.prototype.getAttribute=function(t){return!this[n]||"src"!==t&&"srcset"!==t?f.call(this,t):this[n][t+"Attr"]},HTMLImageElement.prototype.setAttribute=function(t,e){!this[n]||"src"!==t&&"srcset"!==t?g.call(this,t,e):this["src"===t?"src":t+"Attr"]=String(e)})}function s(t,r){var i=!A&&!t;if(r=r||{},t=t||"img",a&&!r.skipTest)return!1;"string"==typeof t?t=document.querySelectorAll("img"):"length"in t&&(t=[t]);for(var c=0;c<t.length;c++)t[c][n]=t[c][n]||r,e(t[c]);i&&(document.body.addEventListener("load",function(t){"IMG"===t.target.tagName&&s(t.target,{skipTest:r.skipTest})},!0),A=!0,t="img"),r.watchMQ&&window.addEventListener("resize",s.bind(null,t,{skipTest:r.skipTest}))}var n="data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",c=/(object-fit|object-position)\s*:\s*([-\w\s%]+)/g,o=new Image,l="object-fit"in o.style,a="object-position"in o.style,u="string"==typeof o.currentSrc,f=o.getAttribute,g=o.setAttribute,A=!1;return s.supportsObjectFit=l,s.supportsObjectPosition=a,i(),s}();

/*! waitForImages - Custom Modified Version */
(function(a){"function"===typeof define&&define.amd?define(["jquery"],a):"object"===typeof exports?module.exports=a(require("jquery")):a(jQuery)})(function(a){a.waitForImages={hasImageProperties:["backgroundImage","listStyleImage","borderImage","borderCornerImage","cursor"],hasImageAttributes:["srcset"]};a.expr[":"]["has-src"]=function(c){return a(c).is('img[src][src!=""]')};a.expr[":"].uncached=function(c){return a(c).is(":has-src")?!c.complete:!1};a.fn.waitForImages=function(){var c=0,l=0,m=a.Deferred(),e,g,d;a.isPlainObject(arguments[0])?(d=arguments[0].waitForAll,g=arguments[0].each,e=arguments[0].finished):1===arguments.length&&"boolean"===a.type(arguments[0])?d=arguments[0]:(e=arguments[0],g=arguments[1],d=arguments[2]);e=e||a.noop;g=g||a.noop;d=!!d;if(!a.isFunction(e)||!a.isFunction(g))throw new TypeError("An invalid callback was supplied.");this.each(function(){var h=a(this),k=[],n=a.waitForImages.hasImageProperties||[],p=a.waitForImages.hasImageAttributes||[],q=/url\(\s*(['"]?)(.*?)\1\s*\)/g;d?h.find("*").addBack().each(function(){var b=a(this);b.is("img:has-src")&&!b.is("[srcset]")&&k.push({src:b.attr("src"),element:b[0]});a.each(n,function(a,c){var e=b.css(c),f;if(!e)return!0;for(;f=q.exec(e);)k.push({src:f[2],element:b[0]})});a.each(p,function(a,c){if(!b.attr(c))return!0;k.push({src:b.attr("src"),srcset:b.attr("srcset"),sizes:b.attr("sizes"),element:b[0]})})}):h.find("img:has-src").each(function(){k.push({src:this.src,element:this})});c=k.length;l=0;0===c&&(e.call(h[0]),m.resolveWith(h[0]));var t="srcset"in document.createElement("img")&&"sizes"in document.createElement("img");a.each(k,function(b,f){var d=new Image;a(d).one("load.waitForImages error.waitForImages",function r(b){b=[l,c,"load"==b.type];l++;g.apply(f.element,b);m.notifyWith(f.element,b);a(this).off("load.waitForImages error.waitForImages",r);if(l==c)return e.call(h[0]),m.resolveWith(h[0]),!1});f.srcset&&t&&(d.srcset=f.srcset,d.sizes=f.sizes);d.src=f.src})});return m.promise()}});