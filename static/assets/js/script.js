function scrollDown() {
    document.getElementById('scroll').scrollTop = document.getElementById('scroll').scrollHeight
    console.log('functionis called!');
    window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight);
}