from fastapi import APIRouter, HTTPException, status, Depends
import ormar_models
from ormar.exceptions import NoMatch
import main


router = APIRouter(prefix='/application', tags=['Application'])


@router.post("/application/", response_model=ormar_models.Application)
async def create_application(application: ormar_models.ApplicationRequest, user:ormar_models.User = Depends(main.current_active_user)):
    
    user_sid = user.sid
    
    try:
        already_present = await Application.objects.first(Application.reg_number==application.reg_number)
        if already_present:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='application for this reg_number already exists')
    except NoMatch:
        pass

    new_application = Application(sid=user_sid, reg_number=application.reg_number, is_approved=False,
                                  is_car=application.is_car, is_bike=application.is_bike)

    await new_application.save()
    return new_application