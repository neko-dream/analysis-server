from openapi_server.data_models.models import Opinions, RepresentativeOpinions, TalkSessionReportHistories, TalkSessions, TalkSessionReports
from openapi_server.models.reports_generates_post_request import ReportsGeneratesPostRequest

from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine
from sqlalchemy import select, insert
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import os
from datetime import datetime, timedelta, timezone

import boto3
import uuid6

client = None

region_name = os.getenv('AWS_REGION', '')
model_id = os.getenv('MODEL_ID', '')

client = boto3.client(
        service_name="bedrock-runtime",
        region_name="ap-northeast-1",
        endpoint_url="https://bedrock-runtime.ap-northeast-1.amazonaws.com"
    )
inferenceConfig = ({"maxTokens": 1000, "temperature": 0.0})
system = [{"text": "あなたは優秀なデータアナリストです。客観的にデータを見てください。"}]

Session = None

def completion(new_message_text:str, settings_text:str = '', past_messages:list = []):
    new_message = {"role": "user", "content": [{"text": new_message_text}]}
    past_messages.append(new_message)

    result = client.converse(
        modelId=model_id,
        messages=past_messages,
        inferenceConfig=inferenceConfig,
        system=system
    )
    response_message = {"role": "assistant", "content": str(result["output"]["message"]["content"][0]["text"])}
    past_messages.append(response_message)
    response_message_text = str(result["output"]["message"]["content"][0]["text"])
    return response_message_text, past_messages


def prepare_dataset(session, talk_session_id: str):
    Session = session
    theme = ''
    text = ''
    # group_names = ["いちご","レモン","ぶどう","すいか"]
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    # 5
    rank_limit = 3
    with Session() as session:
        result = session.query(RepresentativeOpinions, Opinions).\
            join(Opinions, Opinions.opinion_id == RepresentativeOpinions.opinion_id).\
            where(RepresentativeOpinions.talk_session_id == talk_session_id, RepresentativeOpinions.rank < rank_limit).\
            order_by(RepresentativeOpinions.group_id, RepresentativeOpinions.rank).\
            all()
        # print('result---------------')
        # print(result)
        # text = 'グループ名,投稿の内容,グループにおける代表順位(0~4の値があり、値が小さい方が代表性が高い。また順位が一個後になるたびに重要度が1/2になると考えてください)\n'
        text = 'group_name,contents,rank\n'
        for row in result:
            # talk_session_id = row[0].talk_session_id
            group_id = row[0].group_id
            group_name = group_names[group_id]
            content = row[1].content
            rank = row[0].rank
            agree_count = row[0].agree_count
            if agree_count > 0:
                row_text = f'{group_name},{content},{rank}'
                text += row_text + '\n'
        talk_session_row = session.query(TalkSessions)\
                .where(TalkSessions.talk_session_id == talk_session_id)\
                .one()
        theme = talk_session_row.theme
        description = talk_session_row.description

    template_summarize = f"""
    # テーマ: {theme}

    # セッションの説明(id: {talk_session_id})
    ```
    {description}
    ```

    下記はセッションの中の一部の代表意見をグループごとに抽出したcsvのテーブルデータです。
    それぞれカラムの説明をします。\n
    group_name: グループ名\n
    contents: 投稿内容\n
    rank: グループにおける代表順位\n
    特にrankは0~4の値があり、値が小さい方が代表性が高い。また順位が一個後になるたびに重要度が1/2になると考えてください。\n

    以下はこの形式のデータの、あるグループの分析です。
    START EXAMPLES
    input_table_row = "A,大人が夜でも楽しめるような場所もあると良いかも,0\nA,何も置かれていない芝生だからこそ自由に遊べると思うので、今のままで良いと思う,1\nA,普通に子供の笑顔はみんなにとっての幸せなので、作るべき,2"
    interpretation_output = "グループAは大人が夜でも楽しめるような場所もあると良いという意見が最も強く、また芝生を自由に使えることが価値であると考える。一方で、子供の笑顔が幸せをもたらすという意見も存在し、遊具の設置に賛成する声もある。"
    END EXAMPLES

    csvのテーブルデータ:
    ```
    {text}
    ```

    # 上記データについて以下のようにまとめてください
    - あなたは優秀なデータ分析者です
    - csvのテーブルデータから言えることのみを客観的に抽出するようにしてください
    - テーブルデータに情報がない場合は情報がないことを指摘したレポートにしてください
    - グループごとに代表意見の一覧を参考にして要約してください
    - グループ名も付与してかつグループを一言でまとめた段落にする
    - テーマと分析結果をもとにタイトルを考えてください
    - 全体的な課題の段落も作ってください
    - 最後にまとめを書いてください
    - rankの具体的な数字は文章に表さなくて大丈夫ですが、それぞれの代表意見を考慮してグループごとに考察もあるとより良いです
    markdownを用いてブログ記事風にレポートをまとめてください。

    """
    summarize_text, past = completion(template_summarize, '', [])

    with Session() as session:
        now = datetime.now()
        JST = timezone(timedelta(hours=+9), 'JST')
        dt_now = now.astimezone(JST)
        j_now = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
        desc =  f'\n\n---\n\n**注意:** これはAIによって生成された文章です。\n\nレポートの最終更新日時は{j_now}です。'
        summarize_text = summarize_text+desc
        stmt = postgresql.insert(TalkSessionReports).values([
            dict(
                talk_session_id = talk_session_id,
                report = summarize_text,
                created_at = now,
                updated_at = now,
            )
        ])

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[TalkSessionReports.talk_session_id],
            set_=dict(
                report = stmt.excluded.report,
                updated_at=stmt.excluded.updated_at
            ),
        )

        history_id = uuid6.uuid7()
        history_stmt = insert(TalkSessionReportHistories).values(
            talk_session_report_history_id = history_id,
            talk_session_id = talk_session_id,
            report = summarize_text,
            created_at = now
        )

        result = session.execute(upsert_stmt)
        result2 = session.execute(history_stmt)

        session.commit()


def reports_generates(session, reports_generates_post_request: ReportsGeneratesPostRequest):
    prepare_dataset(session, reports_generates_post_request.talk_session_id)