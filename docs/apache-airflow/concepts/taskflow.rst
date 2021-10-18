 .. Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

 ..   http://www.apache.org/licenses/LICENSE-2.0

 .. Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.

TaskFlow
========

.. versionadded:: 2.0

If you write most of your DAGs using plain Python code rather than Operators, then the TaskFlow API will make it much easier to author clean DAGs without extra boilerplate, all using the ``@task`` decorator.

TaskFlow takes care of moving inputs and outputs between your Tasks using XComs for you, as well as automatically calculating dependencies - when you call a TaskFlow function in your DAG file, rather than executing it, you will get an object representing the XCom for the result (an ``XComArg``), that you can then use as inputs to downstream tasks or operators. For example::

    from airflow.decorators import task
    from airflow.operators.email import EmailOperator

    @task
    def get_ip():
        return my_ip_service.get_main_ip()

    @task
    def compose_email(external_ip):
        return {
            'subject':f'Server connected from {external_ip}',
            'body': f'Your server executing Airflow is connected from the external IP {external_ip}<br>'
        }

    email_info = compose_email(get_ip())

    EmailOperator(
        task_id='send_email',
        to='example@example.com',
        subject=email_info['subject'],
        html_content=email_info['body']
    )

Here, there are three tasks - ``get_ip``, ``compose_email``, and ``send_email``.

The first two are declared using TaskFlow, and automatically pass the return value of ``get_ip`` into ``compose_email``, not only linking the XCom across, but automatically declaring that ``compose_email`` is *downstream* of ``get_ip``.

``send_email`` is a more traditional Operator, but even it can use the return value of ``compose_email`` to set its parameters, and again, automatically work out that it must be *downstream* of ``compose_email``.

You can also use a plain value or variable to call a TaskFlow function - for example, this will work as you expect (but, of course, won't run the code inside the task until the DAG is executed - the ``name`` value is persisted as a task parameter until that time)::

    @task
    def hello_name(name: str):
        print(f'Hello {name}!')

    hello_name('Airflow users')

If you want to learn more about using TaskFlow, you should consult :doc:`the TaskFlow tutorial </tutorial_taskflow_api>`.

.. _concepts/taskflow:syntax_comparison:

Syntax Comparison - Taskflow vs. Traditional
--------------------------------------------

One concept that is important to understand about the Taskflow API is the use of ``XComArg`` and implicit dependencies that might not be intuitive at first glance.  Consider the following code block::

  @dag(
      'xcom_testing',
      start_date=datetime(2021, 1, 1),
      max_active_runs=10,
      schedule_interval='0 0 * * *',
      default_args=default_args,
      catchup=False,
      render_template_as_native_obj=True
  )
  def xcom_testing_dag():
      @task
      def set_const():
          return 10

      @task
      def print_const1(some_const):
          print(some_const)

      @task
      def print_const2(some_const):
          print(some_const)

      const = set_const()
      print_const1(const) >> print_const2(const)

The graph created from the above codeblock looks like this::

                ┌────────────┐
       ┌───────►│print_const1├─────────┐
       │        └────────────┘         │
       │                               ▼
  ┌────┴────┐                    ┌────────────┐
  │set_const├───────────────────►│print_const2│
  └─────────┘                    └────────────┘

We can clearly see that there is a dependency between ``print_const1`` and ``print_const2``, because of the bitshift operator that connects the two tasks.  But, it might be confusing to some users that there are dependencies created between ``set_const`` and each of the ``print_const`` tasks.

The reason why this happens is because the purpose of the expression ``print_const1(set_const)``, from the code block above, is two-fold. Not only does this operation create XCom pass from ``set_const`` and its return value to ``print_const1``, it also creates the dependency that must exist between these two operators.

We know logically that in order for ``set_const`` to pass its result to ``print_const``, ``set_const`` must have executed first, and Airflow is intelligent enough to know this implicit dependency.  Through the Taskflow API syntax and the supporting backend code that is described in this document, Airflow will create that dependency automatically.

More succinctly, the most important thing to note from the explanation above is that ``print_const1(set_const)`` sets the return value of ``set_const`` to be passed as an XCom to ``print_const1``, and also sets the dependency between the two tasks (equivalent to ``set_const >> print_xcom1``), in the same operation.  In order to access the return value that was passed as XCom, we make a parameter for the task function that is receiving the XCom, and give it an arbitrary name to be referenced within that function.

If we're comparing this to the old style of Airflow syntax (pre-taskflow), the equivalent would be as such::

  ...
  def set_const():
    return 10

  def xcom_print(ti):
      xcom = ti.xcom_pull(key="return_value", task_ids="set_const")
      print(xcom)

  with DAG(
      'xcom_testing_original',
      start_date=datetime(2021, 1, 1),
      max_active_runs=10,
      schedule_interval='0 0 * * *',
      default_args=default_args,
      catchup=False,
      render_template_as_native_obj=True
  ) as dag:
      task_1 = PythonOperator(
          task_id="set_const",
          python_callable=set_const
      )

      task_2 = PythonOperator(
          task_id="print_const1",
          python_callable=xcom_print
      )

      task_3 = PythonOperator(
          task_id="print_const2",
          python_callable=xcom_print
      )

      task_1 >> task_2
      task_1 >> task_3
      task_2 >> task_3

History
-------

The TaskFlow API is new as of Airflow 2.0, and you are likely to encounter DAGs written for previous versions of Airflow that instead use ``PythonOperator`` to achieve similar goals, albeit with a lot more code.

More context around the addition and design of the TaskFlow API can be found as part of its Airflow Improvement Proposal
`AIP-31: "TaskFlow API" for clearer/simpler DAG definition <https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=148638736>`_
