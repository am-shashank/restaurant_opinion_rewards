function getLocation() {
    if (navigator.geolocation) {
        return navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        throw "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    return {
        'latitude': position.coords.latitude,
        'longitude': position.coords.longitude
    }
}