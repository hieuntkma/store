function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//get csrftoken
function getCSRFTokenValue() {
    const csrftoken = getCookie('csrftoken');
    return csrftoken;
}


//  get cart item
function loadCartItems() {
    fetch('/cart/api/cart-items/')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('cart-table-body');
            const shipping = 40000;
            let subtotal = 0;
            let html = ``;

            // ✅ Truy cập đúng cấu trúc dữ liệu
            const items = data.data?.items || [];
            const total_all_item_price = data.data?.total_all_item_price || 0;

            if (!items.length) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">Giỏ hàng trống</td></tr>`;
                return;
            }

            items.forEach(item => {
                subtotal += item.total_item_price;

                html += `
                <tr data-product-uuid="${item.product_uuid}" class="align-middle">
                    <td>
                        <img src="${item.thumbnail}" alt="ảnh sản phẩm" class="rounded" style="width: 70px; height: 70px; object-fit: cover;">
                    </td>
                    <td class="fw-semibold product-name">${item.name}</td>
                    <td class="product-price">${item.unit_price.toLocaleString()}₫</td>
                    <td class="product-quantity">${item.quantity}</td>
                    <td class="fw-bold">${item.total_item_price.toLocaleString()}₫</td>
                </tr>
            `;
            });

            const total = subtotal + shipping;

            html += `
            <tr class="summary-row">
                <td colspan="4">Tạm tính</td>
                <td>${subtotal.toLocaleString()}₫</td>
            </tr>
            <tr class="summary-row">
                <td colspan="4">Phí vận chuyển</td>
                <td>${shipping.toLocaleString()}₫</td>
            </tr>
            <tr class="summary-row border-top border-2">
                <td colspan="4" class="text-uppercase text-dark h5">Tổng cộng</td>
                <td class="py-4 h5 text-dark fw-bold" id="total-price" style="font-family: inherit; font-weight: 600;">
                    <span style="font-family: inherit;">${total.toLocaleString()}₫</span>
                </td>
            </tr>
        `;

            tbody.innerHTML = html;
        })
        .catch(err => {
            console.error("Lỗi khi tải giỏ hàng:", err);
            document.getElementById('cart-table-body').innerHTML = `<tr><td colspan="5" class="text-danger text-center">Không thể tải dữ liệu giỏ hàng.</td></tr>`;
        });
}

$(document).ready(loadCartItems);

//send order data
$(document).ready(function () {
    $("#order-btn").on("click", function () {
        const first_name = $("input[name=first_name]").val().trim();
        const last_name = $("input[name=last_name]").val().trim();
        const delivery_address = $("input[name=delivery_address]").val().trim();
        const phone = $("input[name=phone]").val().trim();
        const email = $("input[name=email]").val().trim();
        const note = $("textarea").val();
        const ship = 40000
        // ✅ Kiểm tra các trường bắt buộc
        let valid = true;
        $("input[required]").each(function () {
            if (!$(this).val().trim()) {
                $(this).addClass("is-invalid");
                valid = false;
            } else {
                $(this).removeClass("is-invalid");
            }
        });

        if (!valid) {
            return;
        }

        const cartItems = [];
        const shipping = 40000;

        $("#cart-table-body tr[data-product-uuid]").each(function () {
            const $row = $(this);
            cartItems.push({
                product_uuid: $row.attr("data-product-uuid"),
                name: $row.find(".product-name").text(),
                unit_price: parseInt($row.find(".product-price").text().replace(/[^\d]/g, '')),
                quantity: parseInt($row.find(".product-quantity").text())
            });
        });

        if (cartItems.length === 0) {
            Swal.fire("🛒 Giỏ hàng rỗng!", "Bạn cần thêm sản phẩm trước khi đặt hàng.", "warning");
            return;
        }

        const data = {
            first_name,
            last_name,
            delivery_address,
            phone,
            email,
            note,
            shipping_price: shipping,
            total_price: shipping + cartItems.reduce((sum, item) => sum + item.unit_price * item.quantity, 0),
            items: cartItems
        };

        const orderUrl = $("#order-btn").data("order-url");

        // ✅ SweetAlert confirm trước khi gửi đơn hàng
        Swal.fire({
            title: "Xác nhận đặt hàng?",
            text: "Bạn có chắc chắn muốn gửi đơn hàng này không?",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Đặt hàng",
            cancelButtonText: "Huỷ",
        }).then((result) => {
            if (result.isConfirmed) {
                // ✅ Gửi AJAX sau khi người dùng xác nhận
                $.ajax({
                    url: orderUrl,
                    type: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFTokenValue()
                    },
                    contentType: "application/json",
                    data: JSON.stringify(data),
                    success: function (res) {
                        if (res.success) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Đặt hàng thành công!',
                                text: 'Cảm ơn bạn đã đặt hàng.',
                                confirmButtonText: 'Xem đơn hàng'
                            }).then(() => {
                                window.location.href = "/account/my-order";
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Lỗi',
                                text: res.message || 'Đặt hàng thất bại, vui lòng thử lại.'
                            });
                        }
                    },
                    error: function (xhr) {
                        Swal.fire("Lỗi", "Không thể gửi đơn hàng: " + xhr.responseText, "error");
                    }
                });
            }
        });
    });
});