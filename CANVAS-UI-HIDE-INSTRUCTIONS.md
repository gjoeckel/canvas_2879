# Canvas UI Hide CSS - Instructions

This CSS file hides all Canvas UI elements (navigation, headers, sidebars) so that only the page content is visible.

## Module 1 Canvas Page URL
https://usucourses.instructure.com/courses/2879/modules/items/121441

## Method 1: Browser Extension (Recommended)

### Using Stylus Extension

1. Install the **Stylus** browser extension:
   - Chrome: https://chrome.google.com/webstore/detail/stylus/clngdbkpkpeebahjckkjfobafhncgmne
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/styl-us/

2. Open Stylus and click "Write new style"

3. Set the URL pattern to: `https://usucourses.instructure.com/courses/2879/*`

4. Copy and paste the contents of `hide-canvas-ui.css` into the style editor

5. Save the style

6. Visit the Canvas page - the UI will be automatically hidden!

## Method 2: Bookmarklet

1. Create a bookmark in your browser (name it "Hide Canvas UI")

2. Edit the bookmark and set the URL to this bookmarklet:

```
javascript:(function(){if(document.getElementById('hide-canvas-ui-styles')){alert('Canvas UI hide CSS is already active!');return;}const style=document.createElement('style');style.id='hide-canvas-ui-styles';style.textContent='header#header,header#mobile-header,#mobileContextNavContainer{display:none!important}.ic-app-nav-toggle-and-crumbs,#breadcrumbs,.ic-app-crumbs,#courseMenuToggle,button#courseMenuToggle{display:none!important}#left-side,.ic-app-course-menu,#sticky-container{display:none!important}#right-side-wrapper,#right-side{display:none!important}#easy_student_view,.mobile-header-student-view,#mobile-student-view,.mobile-header-hamburger,.mobile-header-title,.mobile-header-space,.mobile-header-arrow{display:none!important}#nutrition_facts_container,#nutrition_facts_mobile_container{display:none!important}.ic-app-header__main-navigation,.ic-app-header__secondary-navigation,.ic-app-header__logomark-container,#global_nav_tray_container,#global_nav_tour{display:none!important}#flash_message_holder,#flash_screenreader_holder,#skip_navigation_link,#aria_alerts{display:none!important}footer,#footer,iframe#post_message_forwarding,#StudentTray__Container,#react-router-portals,#instructure_ajax_error_box,.ic-Layout-watermark{display:none!important}#wrapper.ic-Layout-wrapper{margin-left:0!important;padding-left:0!important}#main.ic-Layout-columns{margin-left:0!important;padding-left:0!important}#content-wrapper{margin-left:0!important;padding-left:0!important}#content.ic-Layout-contentMain{margin-left:0!important;padding-left:20px!important;padding-right:20px!important;max-width:100%!important;width:100%!important}#wiki_page_show,#content{display:block!important;width:100%!important;max-width:1200px!important;margin:0 auto!important;padding:20px!important}.user_content{padding:20px!important}.right-of-crumbs{display:none!important}';document.head.appendChild(style);alert('Canvas UI hidden! Only page content is now visible.');})();
```

3. When on a Canvas page, click the bookmarklet to hide the UI

## Method 3: Browser Developer Tools

1. Open the Canvas page

2. Open Developer Tools (F12 or Right-click → Inspect)

3. Go to the Console tab

4. Paste the code from `canvas-ui-hide-bookmarklet.js` and press Enter

## Testing

Test on the Module 1 page:
https://usucourses.instructure.com/courses/2879/modules/items/121441

After applying the CSS, you should see:
- ✅ Only the page content visible
- ✅ No header/navigation
- ✅ No sidebars
- ✅ No breadcrumbs
- ✅ Content centered and properly spaced

