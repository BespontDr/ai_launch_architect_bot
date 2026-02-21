from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.db import Database
from keyboards.inline import get_full_strategy_keyboard, skip_keyboard
from services.openai_service import OpenAIService
from services.prompt_builder import build_free_prompt

router = Router()


class LaunchStates(StatesGroup):
    idea = State()
    niche = State()
    audience = State()
    product = State()


QUESTIONS = {
    LaunchStates.idea: "Опишите вашу идею проекта или личного бренда:",
    LaunchStates.niche: "Укажите нишу, в которой вы хотите развиваться:",
    LaunchStates.audience: "Кто ваша целевая аудитория?",
    LaunchStates.product: "Как вы планируете монетизировать проект?",
}


@router.callback_query(F.data == "start_launch")
async def start_launch(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    user = callback.from_user
    await db.create_user_if_not_exists(user.id, user.username, user.full_name)

    await state.set_state(LaunchStates.idea)
    await callback.message.answer(QUESTIONS[LaunchStates.idea], reply_markup=skip_keyboard())
    await callback.answer()


@router.callback_query(F.data == "skip_step")
async def skip_step(callback: CallbackQuery, state: FSMContext, db: Database, openai_service: OpenAIService) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer("Сначала нажмите «🚀 Запустить проект».", show_alert=True)
        return

    state_obj = _state_from_raw(current_state)
    if state_obj is None:
        await state.clear()
        await callback.answer("Состояние устарело, начните заново.", show_alert=True)
        return
    await _save_answer(db, callback.from_user.id, state_obj, None)
    await _go_next(state, callback.message, state_obj, callback.from_user.id, db, openai_service)
    await callback.answer()


@router.message(LaunchStates.idea)
async def save_idea(message: Message, state: FSMContext, db: Database, openai_service: OpenAIService) -> None:
    await _save_answer(db, message.from_user.id, LaunchStates.idea, message.text)
    await _go_next(state, message, LaunchStates.idea, message.from_user.id, db, openai_service)


@router.message(LaunchStates.niche)
async def save_niche(message: Message, state: FSMContext, db: Database, openai_service: OpenAIService) -> None:
    await _save_answer(db, message.from_user.id, LaunchStates.niche, message.text)
    await _go_next(state, message, LaunchStates.niche, message.from_user.id, db, openai_service)


@router.message(LaunchStates.audience)
async def save_audience(message: Message, state: FSMContext, db: Database, openai_service: OpenAIService) -> None:
    await _save_answer(db, message.from_user.id, LaunchStates.audience, message.text)
    await _go_next(state, message, LaunchStates.audience, message.from_user.id, db, openai_service)


@router.message(LaunchStates.product)
async def save_product(message: Message, state: FSMContext, db: Database, openai_service: OpenAIService) -> None:
    await _save_answer(db, message.from_user.id, LaunchStates.product, message.text)
    await _go_next(state, message, LaunchStates.product, message.from_user.id, db, openai_service)


def _state_from_raw(raw_state: str) -> State | None:
    mapping = {
        LaunchStates.idea.state: LaunchStates.idea,
        LaunchStates.niche.state: LaunchStates.niche,
        LaunchStates.audience.state: LaunchStates.audience,
        LaunchStates.product.state: LaunchStates.product,
    }
    return mapping.get(raw_state)


async def _save_answer(db: Database, telegram_id: int, state_name: State, value: str | None) -> None:
    field_map = {
        LaunchStates.idea: "idea",
        LaunchStates.niche: "niche",
        LaunchStates.audience: "audience",
        LaunchStates.product: "product",
    }
    await db.update_user_field(telegram_id, field_map[state_name], value)


async def _go_next(
    state: FSMContext,
    message: Message,
    current_state: State,
    telegram_id: int,
    db: Database,
    openai_service: OpenAIService,
) -> None:
    order = [LaunchStates.idea, LaunchStates.niche, LaunchStates.audience, LaunchStates.product]
    current_idx = order.index(current_state)

    if current_idx < len(order) - 1:
        next_state = order[current_idx + 1]
        await state.set_state(next_state)
        await message.answer(QUESTIONS[next_state], reply_markup=skip_keyboard())
        return

    await state.clear()

    user = await db.get_user(telegram_id)
    if user is None:
        await message.answer("Ошибка: пользователь не найден. Нажмите /start и попробуйте снова.")
        return

    prompt = build_free_prompt(user)
    try:
        result = await openai_service.generate_text(prompt)
    except RuntimeError as exc:
        await message.answer(str(exc))
        return

    await message.answer(result, reply_markup=get_full_strategy_keyboard())
