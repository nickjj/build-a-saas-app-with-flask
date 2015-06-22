var pluralize = function (word, count) {
    if (count === 1) {
        return word;
    }

    return `${word}s`;
};

module.exports = pluralize;
