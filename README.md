МОБИЛЬНАЯ ОЧЕРЕДЬ
  B2C сервис для оптимизации человеческих очередей


Проблема: 
Живые человеческие очереди обычно отбирают 10-90 минут у людей. 
Являются источником распространения болезней.
Бизнес не экономит на исполнителях. 
Бизнес вынужденно расширяет время приема граждан. 
Решение: 
	Электронные очереди в смартфоне. 
Каждый пользователь может используя бота записаться к исполнителю(или организации), и следить за статусом очереди онлайн, по окончанию приема исполнитель (или посетитель) отмечают окончание процедуры и следующему посетителю прийдет уведомление

Реализация: 
	v0.1 - telegram bot
	v0.5 - web application + QR code

Описание функционала:

	В приложении есть две роли пользователей Посетитель и Исполнитель.
	Исполнитель:
Создает новую пустую очередь с помощью команды: /new очередь
Очищает очередь: /clear очередь
Закрывает очередь на запись: /stop очередь
Удаляет очередь: /delete очередь
Отработал одного клиента: /done 
Отработал N клиентов: /done N
Задать время, через которое пользователь автоматически удаляется или становиться в конец очереди: /onetimedelta

Посетитель:
	Посмотреть сколько всего людей в очереди: /check очередь
	Стать в очередь: /in очередь
	Посмотреть в каких очередях стоишь и какой номер в каждой: /me
	Узнать через сколько времени моя очередь: /checktime очередь
	Уведомить меня, если я следующий: /alert очередь
	Показать детали очереди (имя и время когда записался каждого кто в очереди) /details очередь
	Сообщить боту, что я не попаду на прием: /skip очередь
	Сообщить боту, что я уже окончил прием: /done очередь
