/*!
* Start Bootstrap - Shop Homepage v5.0.6 (https://startbootstrap.com/template/shop-homepage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-shop-homepage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project
document.getElementById('productFilter').addEventListener('input', function () {
	const filter = this.value.toLowerCase();
	const products = document.querySelectorAll('.product-item');

	products.forEach(product => {
		const name = product.querySelector('h5').textContent.toLowerCase();
		if (name.includes(filter)) {
			product.style.display = 'block';
		} else {
			product.style.display = 'none';
		}
	});
});