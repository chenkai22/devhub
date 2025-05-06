from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Ticket


@registry.register_document
class TicketDocument(Document):

    def prepare(self, instance):
        # 添加调试日志
        print(f"Indexing Ticket ID:{instance.id}")
        print(f"Attachments: {instance.attachments_ids}")
        print(f"Status: {instance.get_status_display()}")
        print(f"Deadline: {instance.deadline}")
        prepared_data = super().prepare(instance)
        if instance.deadline:
            prepared_data["deadline"] = instance.deadline.strftime("%Y-%m-%d %H:%M:%S")
        return prepared_data

    suggest = fields.CompletionField()

    title = fields.TextField(analyzer="ik_max_word")  # 使用中文分词器
    ticket_code = fields.KeywordField()
    desc = fields.TextField(analyzer="ik_max_word")
    status_display = fields.KeywordField(attr="get_status_display")
    find_user = fields.IntegerField(attr="find_user_id")
    handler = fields.IntegerField(attr="handler_id")

    attachments = fields.ListField(fields.IntegerField(attr="attachments_ids"))
    deadline = fields.DateField(format="yyyy-MM-dd HH:mm:ss")

    def prepare_suggest(self, instance):
        return {
            "input": [instance.title, instance.ticket_code],
            "weight": 5,
        }

    class Index:
        name = "tickets"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {  # 添加中文建议分析器
                "analyzer": {"my_ik": {"type": "custom", "tokenizer": "ik_max_word"}}
            },
        }

    class Django:
        model = Ticket
        fields = [
            "id",
        ]
