window.addEventListener('load', function(){
    let sidebar = document.querySelector('bits-sidebar')
    let sidebar_button = document.querySelector('#sidebar-button');
    sidebar_button.addEventListener('click', function(){
        sidebar.show_sidebar();
        console.log('show');
    });
});