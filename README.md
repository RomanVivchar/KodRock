Привет! 

Телеграм-бот "Агрегатор занний о процессах химического производства" позволяет сотрудникам завода задавать свои вопросы и отвечать на вопросы коллег.

В боте реализованы следующие функции: 

1) Сотрудники имеют возможность голосовать за лучшие вопросы. 

2) Вопросы отображаются в порядке убывания голосов. 

3) В чат-боте присутствует система тегов, которая позволяет определить тематику вопроса. 

4) Сотрудники имеют возможность находить вопросы по тегам. 

5) Сотрудники имеют возможность возвращаться к своим вопросам и редактировать их. 

6) Сотрудники имеют возможность возвращаться к своим ответам на вопросы и редактировать их. 

7) В чат-боте присутствует система вознаграждения за создание своих вопросов и за ответы на вопросы других сотрудников. Специальная валюта 💎 gems, котрая выдается за создание своих вопросов и ответов на запросы коллег.

8) В чат-боте есть раздел, где отображаются сотрудники, оставившие вопросы или ответы, в порядке уменьшения количества их вопросов или ответов.
В этом разделе указаны колличество вопросов, ответов и контактные данные этих сотрудников. 

9) В чат-боте есть раздел администратора, вход в которой осуществляется через соответствующие логин и пароль.
Данный раздел позволяет осуществлять модерацию или отклонение вопросов, прежде чем они попадут в открытый доступ. 

10) В чат-боте есть раздел администратора, вход в которой осуществляется через соответствующие логин и пароль.
Данный раздел позволяет осуществлять модерацию или отклонение ответов на вопросы, прежде чем они попадут в открытый доступ. 

11) В чат-боте есть раздел администратора, вход в которой осуществляется через соответствующие логин и пароль.
Данный раздел позволяет осуществлять массовые рассылки информации для всех сотрудников. 

12) Сотрудник может открыть свой аккаунт и просмотреть свои личные данные.


Также в файле db.py создан и описан класс Database, с помощью которго осуществлялось все взаимодействие с базой данных  PostgreSQL. 

База данных состоит из следующих таблиц: 

users - columns: user_id, name, last_name, phone_number, email, gems(то есть баланс валюты)

question - columns: question_id, tag, user_id, text, date, is_sent, declined, rating

answer - columns: answer_id, text, user_id, date, question_id, is_sent, declined

admins - columns: login, password, user_id

  


Я думаю стоит отдельно поговорить о разделе администратора и для чего в БД столбцы is_sent, declined.

Раздел администратора предназначен для модерации вопросов и ответов сотрудников. В роли администратора я могу принять или отклонить соответствующие запросы от пользователей. 
Механика сосотит в том, что перед тем, как вопрос(или ответ) попадет в общий доступ, он должен быть приянт админом. Тут то и нам понадобятся столбцы is_sent и declined. 
Default value у них стоит False и True соотвественно. Почему? Логика такова: пока админ не просмотрел не просмотрел вопросы, они не показываются пользователям, следовательно default значение 
столбца declined = True. Как только админ начинает смотреть отправленные вопросы, статус is_sent у всех вопросов становится True, тк он их просмотрел. Далее идет выор админа.
В боте реализована такая схема, что админ должен написать в ответ боту айди вопросов(в коде этим айди присваивается статус declined = False), которые стоит принять(они ему показываются), 
а остальные вопросы, которые админ не указал, будут отклонены(у них так и остается declined = True). Ну и из этого следует, что показываются обычным пользователям только те вопросы, у которых статус
declined = False. 
Однако непонятно, для чего столбец is_sent. Все просто! Админу показываются только те вопросы, у которых is_sent = False, чтобы те вопросы, которые он уже просмотрел и принял по ним решения, больше
ему не показывались. 


На этом краткое описание функций бота закончено! Огромное спасибо за прочтение данного readme!

