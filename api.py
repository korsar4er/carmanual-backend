from flask_restful import Api
from resources.user import UserResource, UsersResource
from resources.auth import (Registration, Login, Confirm,
                            ChangePassword, ForgotPassword,
                            TokenRefresh)
from resources.car import CarsResourse, CarResourse, CarApproveResourse
from resources.part import PartsResource, PartResource
from resources.doc import (DocResource, DocByIdResource,
                           DocsResource, DocApproveResourse)
from resources.upload import UploadImage

api = Api(prefix='/api')

# Route
api.add_resource(Registration, '/registration')
api.add_resource(Login, '/login')
api.add_resource(Confirm, '/confirm/<string:token>', endpoint="confirm")
api.add_resource(ChangePassword, '/changepassword')
api.add_resource(ForgotPassword, '/forgotpassword')
api.add_resource(TokenRefresh, '/tokenrefresh')

api.add_resource(UserResource, '/user')
api.add_resource(UsersResource, '/users')

api.add_resource(CarsResourse, '/cars')
api.add_resource(CarResourse, '/car')
api.add_resource(CarApproveResourse, '/carapprove/<int:id>')

api.add_resource(PartsResource, '/parts')
api.add_resource(PartResource, '/part')

api.add_resource(DocResource, '/doc')
api.add_resource(DocByIdResource, '/doc/<int:id>')
api.add_resource(DocsResource, '/docs')
api.add_resource(DocApproveResourse, '/docapprove/<int:id>')

api.add_resource(UploadImage, '/uploadimage')
