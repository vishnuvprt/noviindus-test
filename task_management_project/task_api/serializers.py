from rest_framework import serializers
from task_api.models import Task
from accounts.serializers import UserListSerializer


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_details = UserListSerializer(source='assigned_to', read_only=True)
    assigned_by_details = UserListSerializer(source='assigned_by', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_by',
            'assigned_to_details', 'assigned_by_details', 'due_date', 
            'status', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
                        'title': {
                            'required': True,
                            'allow_blank': False,
                            'error_messages': {
                                'required': 'Please enter title.',
                                'blank': 'Title cannot be blank.'
                            }
                        },
                        'description': {
                            'required': True,
                            'allow_blank': False,
                            'error_messages': {
                                'required': 'Please enter description.',
                                'blank': 'Description cannot be blank.'
                            }
                        },
                        'assigned_to': {
                            'required': True,
                            'allow_null': False,
                            'error_messages': {
                                'required': 'Please assign the task to a user.',
                                'null': 'Assigned user cannot be null.'
                            }
                        },
                        'due_date': {
                            'required': True,
                            'allow_null': False,
                            'error_messages': {
                                'required': 'Please enter due date.',
                                'null': 'Due date cannot be null.'
                            }
                        },
                    }
    
    def create(self, validated_data):
        # Set the current user as the one who assigned the task
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskCompletionSerializer(serializers.ModelSerializer):
    completion_report = serializers.CharField(required=False)
    worked_hours = serializers.DecimalField(required=False, max_digits=5, decimal_places=2)
    
    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']
    
    def validate(self, data):
        errors = {}
        if data.get('status') == 'completed':
            if not data.get('completion_report'):
                errors['completion_report'] = "Completion report is required when marking a task as completed."
                
            if not data.get('worked_hours'):
                errors['worked_hours'] = "Worked hours are required when marking a task as completed."
                
        if errors:
            raise serializers.ValidationError(errors)
        return data
    
    def update(self, instance, validated_data):
        status = validated_data.get('status')

        if status == 'completed':
            instance.mark_completed(
                completion_report=validated_data.get('completion_report'),
                worked_hours=validated_data.get('worked_hours')
            )
        elif status == 'in_progress':
            instance.status = 'in_progress'
            instance.save()
        else:
            return super().update(instance, validated_data)

        return instance


class TaskReportSerializer(serializers.ModelSerializer):
    assigned_to_details = UserListSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to_details', 
            'status', 'completion_report', 'worked_hours', 
            'completed_at', 'due_date'
        ]
        read_only_fields = fields