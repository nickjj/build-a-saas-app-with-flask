var typewatch = function () {
    var timer = 0;

    return function (callback, ms) {
        clearTimeout(timer);
        return timer = setTimeout(callback, ms);
    };
};

module.exports = typewatch();
