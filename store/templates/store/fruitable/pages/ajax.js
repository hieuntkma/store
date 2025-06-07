$(document).ready(function () {
    $(".heartIcon").click(function () {
        // Lấy ID của bài thi từ thuộc tính data
        var examId = $(this).data("exam-id");
        console.log(examId)
        removeFavoriteExam(examId);
    });

    //get cookie
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

    // Hàm xóa FavoriteExam
    function removeFavoriteExam(examId) {
        $.ajaxSetup({
            headers: {
                'X-CSRFToken': getCSRFTokenValue(),
            },
            tryCount: 0,
            retryLimit: 3,
        });
        var URL = "http://127.0.0.1:8000/dashboard/student/fav_exam/delete/"
        $.ajax({
            url: URL + examId,  // Thay đổi đường dẫn tương ứng
            type: "POST",
            data: {exam_id: examId},
            success: function (response) {
                console.log("Favorite exam removed successfully.");
                window.location.reload();
            },
            error: function (xhr, status, error) {
                console.error("Error removing favorite exam:", error);
            }
        });
    }
});

