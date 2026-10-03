from user import UserService


class PaymentService:

    def make_payment(self):
        user_service = UserService()
        user_service.validate_user()
        print("Payment completed")